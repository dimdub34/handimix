# -*- coding: utf-8 -*-

from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, String
import logging
from datetime import datetime
import numpy as np
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
        self.group_type = pms.WITHOUT_HAND  # default value
        self.nb_handicap_in_group = 0  # default value
        self.HM_gain_ecus = 0
        self.HM_gain_euros = 0
        # joueur a un parametre handicap fixé par l'écran serveur
        if not hasattr(self.joueur, "handicap"):
            self.joueur.handicap = False

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
        self.currentperiod.HM_hand = self.joueur.handicap
        self.currentperiod.HM_group_type = self.group_type
        self.currentperiod.HM_nb_handicap_in_group = self.nb_handicap_in_group
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
        self.currentperiod.HM_public_account = \
            yield(
                self.remote.callRemote("display_decision"))
        self.currentperiod.HM_decision_time = \
            (datetime.now() - debut).seconds
        self.currentperiod.HM_indiv_account = \
            pms.DOTATION - self.currentperiod.HM_public_account
        self.joueur.info(u"{}".format(
            self.currentperiod.HM_public_account))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        """
        Compute the payoff for the period
        :return:
        """
        logger.debug(u"{} Period Payoff".format(self.joueur))

        # indiv
        self.currentperiod.HM_payoff_from_indiv_account = \
            self.currentperiod.HM_indiv_account * pms.RENDEMENT_INDIV

        # coll
        self.currentperiod.HM_payoff_from_public_account = \
            self.currentperiod.HM_public_account_group * pms.RENDEMENT_COLL

        # total
        self.currentperiod.HM_periodpayoff = \
            self.currentperiod.HM_payoff_from_indiv_account + \
            self.currentperiod.HM_payoff_from_public_account

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
        self.HM_gain_euros = float(np.round(float(self.HM_gain_ecus) *
                                      float(pms.TAUX_CONVERSION), 2))
        if pms.EXPECTATION:
            # ajout des expectations
            expectations_payoffs = sum(
                [p.HM_payoff_from_expectation for p in self.repetitions])
            self.joueur.info(u"PP {}, EP {}".format(
                self.HM_gain_euros, expectations_payoffs))
            self.HM_gain_euros += expectations_payoffs
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

    @defer.inlineCallbacks
    def display_group_composition(self):
        yield(self.remote.callRemote("display_group_composition", self.group_type))
        self.joueur.info("Ok")
        self.joueur.remove_waitmode()

    def compute_expectations_payoffs(self):
        logger.debug(u"{} compute_expectations_payoffs".format(self.joueur))
        self.currentperiod.HM_public_account_average_others = \
            int((self.currentperiod.HM_public_account_group -
             self.currentperiod.HM_public_account) / (pms.TAILLE_GROUPES - 1))
        self.currentperiod.HM_payoff_from_expectation = \
            pms.get_payoff_expectation(
                self.currentperiod.HM_expectation,
                self.currentperiod.HM_public_account_average_others)
        self.joueur.info(u"{}".format(
            self.currentperiod.HM_payoff_from_expectation))
        self.joueur.remove_waitmode()


class RepetitionsHM(Base):
    __tablename__ = 'partie_handimix_repetitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_partie_id = Column(
        Integer,
        ForeignKey("partie_handimix.partie_id"))

    HM_period = Column(Integer)
    HM_treatment = Column(Integer)
    HM_nb_handicap = Column(Integer)
    HM_nb_handicap_in_group = Column(Integer)
    HM_group = Column(String)
    HM_group_type = Column(Integer)
    HM_expectation = Column(Integer)
    HM_indiv_account = Column(Integer)
    HM_public_account = Column(Integer)
    HM_public_account_group = Column(Integer)
    HM_public_account_average_others = Column(Integer)
    HM_decision_time = Column(Integer)
    HM_payoff_from_expectation = Column(Integer)
    HM_payoff_from_indiv_account = Column(Float)
    HM_payoff_from_public_account = Column(Float)
    HM_periodpayoff = Column(Float)
    HM_cumulativepayoff = Column(Float)

    def __init__(self, periode):
        self.HM_treatment = pms.TREATMENT
        self.HM_nb_handicap = pms.NB_HANDICAP
        self.HM_period = periode
        self.HM_decision_time = 0
        self.HM_payoff_from_expectation = 0
        self.HM_payoff_from_indiv_account = 0
        self.HM_payoff_from_public_account = 0
        self.HM_periodpayoff = 0
        self.HM_cumulativepayoff = 0

    def todict(self, joueur=None):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if joueur:
            temp["joueur"] = joueur
        return temp
