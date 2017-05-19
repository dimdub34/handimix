# -*- coding: utf-8 -*-

from twisted.internet import defer
import logging
from collections import OrderedDict
from util import utiltools
from util.utili18n import le2mtrans
import handimixParams as pms
from handimixTexts import trans_HM
from handimixGui import DConfigure, DHandi


logger = logging.getLogger("le2m".format(__name__))


class Serveur(object):
    def __init__(self, le2mserv):
        self.le2mserv = le2mserv

        actions = OrderedDict()
        actions[le2mtrans(u"Configure")] = self._configure
        actions[trans_HM(u"Set Hand.")] = self._set_handicap
        actions[le2mtrans(u"Display parameters")] = \
            lambda _: self.le2mserv.gestionnaire_graphique. \
            display_information2(
                utiltools.get_module_info(pms), u"Paramètres")
        actions[le2mtrans(u"Start")] = lambda _: self._demarrer()
        actions[le2mtrans(u"Display payoffs")] = \
            lambda _: self.le2mserv.gestionnaire_experience.\
            display_payoffs_onserver("handimix")
        self.le2mserv.gestionnaire_graphique.add_topartmenu(
            u"PGG - Handimix", actions)

    def _configure(self):
        screen_conf = DConfigure(self.le2mserv.gestionnaire_graphique.screen)
        if screen_conf.exec_():
            self.le2mserv.gestionnaire_graphique.infoserv(
                [u"Treatment: {}".format(pms.TREATMENTS_NAMES.get(pms.TREATMENT)),
                 u"Group size: {}".format(pms.TAILLE_GROUPES),
                 u"Periods: {}".format(pms.NOMBRE_PERIODES),
                 u"Indiv. account: {} {}".format(pms.RENDEMENT_INDIV, pms.MONNAIE),
                 u"Coll. account: {} {}".format(pms.RENDEMENT_COLL, pms.MONNAIE),
                 u"Conversion rate: 1 ecu = {} euro".format(pms.TAUX_CONVERSION)]
            )
        return

    @defer.inlineCallbacks
    def _demarrer(self):
        """
        Start the part
        :return:
        """
        # check conditions =====================================================
        if self.le2mserv.gestionnaire_joueurs.nombre_joueurs % \
                pms.TAILLE_GROUPES != 0 :
            self.le2mserv.gestionnaire_graphique.display_error(
                trans_HM(u"The number of players is not compatible "
                          u"with the group size"))
            return
        confirmation = self.le2mserv.gestionnaire_graphique.\
            question(u"Démarrer handimix?")
        if not confirmation:
            return

        # init part ============================================================
        yield (self.le2mserv.gestionnaire_experience.init_part(
            "handimix", "PartieHM", "RemoteHM", pms))
        self._tous = self.le2mserv.gestionnaire_joueurs.get_players(
            'handimix')

        # groups
        self.le2mserv.gestionnaire_groupes.former_groupes(
            self.le2mserv.gestionnaire_joueurs.get_players(),
            pms.TAILLE_GROUPES, forcer_nouveaux=True)

        # set parameters on remotes
        yield (self.le2mserv.gestionnaire_experience.run_func(
            self._tous, "configure"))

        # start ================================================================
        for period in range(1 if pms.NOMBRE_PERIODES else 0,
                        pms.NOMBRE_PERIODES + 1):

            if self.le2mserv.gestionnaire_experience.stop_repetitions:
                break

            # init period
            self.le2mserv.gestionnaire_graphique.infoserv(
                [None, u"Période {}".format(period)])
            self.le2mserv.gestionnaire_graphique.infoclt(
                [None, u"Période {}".format(period)], fg="white", bg="gray")
            yield (self.le2mserv.gestionnaire_experience.run_func(
                self._tous, "newperiod", period))
            
            # decision
            yield(self.le2mserv.gestionnaire_experience.run_step(
                u"Décision", self._tous, "display_decision"))

            # compute total amount in the public account by group
            self.le2mserv.gestionnaire_graphique.infoserv(
                trans_HM(u"Total amount by group"))
            for g, m in self.le2mserv.gestionnaire_groupes.get_groupes(
                    "handimix").viewitems():
                total = sum([p.currentperiod.HM_public for p in m])
                for p in m:
                    p.currentperiod.HM_publicgroup = total
                self.le2mserv.gestionnaire_graphique.infoserv(
                    u"G{}: {}".format(g.split("_")[2], total))
            
            # period payoff
            self.le2mserv.gestionnaire_experience.compute_periodpayoffs(
                "handimix")
        
            # summary
            yield(self.le2mserv.gestionnaire_experience.run_step(
                u"Summary", self._tous, "display_summary"))

        # end of part ==========================================================
        yield (self.le2mserv.gestionnaire_experience.finalize_part(
            "handimix"))

    def _set_handicap(self):
        screen_handi = DHandi(self.le2mserv)
        if screen_handi.exec_():
            self.le2mserv.gestionnaire_graphique.infoclt("Handicap")
            for j in self.le2mserv.gestionnaire_joueurs.get_players():
                self.le2mserv.gestionnaire_graphique.infoclt("{}: {}".format(
                    j, j.handicap))