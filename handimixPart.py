# -*- coding: utf-8 -*-

from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, String
import logging
from datetime import datetime
from util.utiltools import get_module_attributes
from server.servbase import Base
from server.servparties import Partie
import handimixParams as pms


logger = logging.getLogger("le2m")


class PartieHM(Partie):
    __tablename__ = "partie_handimix"
    __mapper_args__ = {'polymorphic_identity': 'handimix'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    repetitions = relationship('RepetitionsHM')

    def __init__(self, le2mserv, joueur):
        super(PartieHM, self).__init__("handimix", "HM")
        self._le2mserv = le2mserv
        self.joueur = joueur
        self.HM_gain_ecus = 0
        self.HM_gain_euros = 0
        # joueur a un parametre handicap fixé par l'écran serveur

    @defer.inlineCallbacks
    def configure(self, *args):
        logger.debug(u"{} Configure".format(self.joueur))
        yield (self.remote.callRemote("configure", get_module_attributes(pms)))

    @defer.inlineCallbacks
    def newperiod(self, period):
        """
        Create a new period and inform the remote
        If this is the first period then empty the historic
        :param period:
        :return:
        """
        logger.debug(u"{} New Period".format(self.joueur))
        self.currentperiod = RepetitionsHM(period)
        self.currentperiod.HM_group = self.joueur.groupe
        self._le2mserv.gestionnaire_base.ajouter(self.currentperiod)
        self.repetitions.append(self.currentperiod)
        yield (
            self.remote.callRemote("newperiod", period))
        logger.info(u"{} Ready for periode {}".format(self.joueur, period))

    @defer.inlineCallbacks
    def display_decision(self):
        """
        Display the decision screen on the remote
        Get back the decision
        :return:
        """
        logger.debug(u"{} Decision".format(self.joueur))
        debut = datetime.now()
        self.currentperiod.HM_public = \
            yield(
                self.remote.callRemote("display_decision"))
        self.currentperiod.HM_decisiontime = \
            (datetime.now() - debut).seconds
        self.currentperiod.HM_indiv = \
            pms.DOTATION - self.currentperiod.HM_public
        self.joueur.info(u"{}".format(
            self.currentperiod.HM_public))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        """
        Compute the payoff for the period
        :return:
        """
        logger.debug(u"{} Period Payoff".format(self.joueur))

        # indiv
        self.currentperiod.HM_indivpayoff = \
            self.currentperiod.HM_indiv * pms.RENDEMENT_INDIV

        # coll
        self.currentperiod.HM_publicpayoff = \
            self.currentperiod.HM_publicgroup * pms.RENDEMENT_COLL

        # total
        self.currentperiod.HM_periodpayoff = \
            self.currentperiod.HM_indivpayoff + \
            self.currentperiod.HM_publicpayoff

        # cumulative payoff since the first period
        if self.currentperiod.HM_period < 2:
            self.currentperiod.HM_cumulativepayoff = \
                self.currentperiod.HM_periodpayoff
        else: 
            previousperiod = self.periods[
                self.currentperiod.HM_period - 1]
            self.currentperiod.HM_cumulativepayoff = \
                previousperiod.HM_cumulativepayoff + \
                self.currentperiod.HM_periodpayoff

        # we store the period in the self.periodes dictionnary
        self.periods[self.currentperiod.HM_period] = self.currentperiod

        logger.debug(u"{} Period Payoff {}".format(
            self.joueur, self.currentperiod.HM_periodpayoff))

    @defer.inlineCallbacks
    def display_summary(self, *args):
        logger.debug(u"{} Summary".format(self.joueur))
        yield(
            self.remote.callRemote(
                "display_summary", self.currentperiod.todict()))
        self.joueur.info("Ok")
        self.joueur.remove_waitmode()

    @defer.inlineCallbacks
    def compute_partpayoff(self):
        logger.debug(u"{} Part Payoff".format(self.joueur))

        self.HM_gain_ecus = \
            self.currentperiod.HM_cumulativepayoff
        self.HM_gain_euros = \
            float(self.HM_gain_ecus) * \
            float(pms.TAUX_CONVERSION)
        yield (self.remote.callRemote(
            "set_payoffs", self.HM_gain_euros, self.HM_gain_ecus))

        logger.info(u'{} Part Payoff ecus {} Part Payoff euros {:.2f}'.format(
            self.joueur, self.HM_gain_ecus, self.HM_gain_euros))

    @defer.inlineCallbacks
    def display_expectations(self):
        """
        Expectations, except for treatments with a vote step
        :return:
        """
        logger.debug(u"{} display_expectation".format(self.joueur))
        self.currentperiod.HM_expectation = \
            yield (self.remote.callRemote("display_expectations"))
        self.joueur.info(u"{}".format(self.currentperiod.HM_expectation))
        self.joueur.remove_waitmode()


class RepetitionsHM(Base):
    __tablename__ = 'partie_handimix_repetitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_partie_id = Column(
        Integer,
        ForeignKey("partie_handimix.partie_id"))

    HM_period = Column(Integer)
    HM_treatment = Column(Integer)
    HM_group = Column(String)
    HM_group_type = Column(Integer)
    HM_indiv_account = Column(Integer)
    HM_public_account = Column(Integer)
    HM_public_account_group = Column(Integer)
    HM_decision_time = Column(Integer)
    HM_payoff_from_indiv_account = Column(Float)
    HM_payoff_from_public_account = Column(Float)
    HM_expectation = Column(Integer)
    HM_periodpayoff = Column(Float)
    HM_cumulativepayoff = Column(Float)

    def __init__(self, periode):
        self.HM_treatment = pms.TREATMENT
        self.HM_period = periode
        self.HM_decision_time = 0
        self.HM_periodpayoff = 0
        self.HM_cumulativepayoff = 0

    def todict(self, joueur=None):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if joueur:
            temp["joueur"] = joueur
        return temp
