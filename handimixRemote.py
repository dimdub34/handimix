# -*- coding: utf-8 -*-

from twisted.internet import defer
from client.cltremote import IRemote
import logging
import random
from client.cltgui.cltguidialogs import GuiRecapitulatif
import handimixParams as pms
from handimixGui import GuiDecision, DExpectation, HISTO_WIDTH
import handimixTexts as texts_HM


logger = logging.getLogger("le2m")


class RemoteHM(IRemote):
    """
    Class remote, remote_ methods can be called by the server
    """
    def __init__(self, le2mclt):
        IRemote.__init__(self, le2mclt)

    def remote_configure(self, params):
        logger.info(u"{} Configure".format(self._le2mclt.uid))
        for k, v in params.viewitems():
            setattr(pms, k, v)

    def remote_newperiod(self, period):
        logger.info(u"{} Period {}".format(self._le2mclt.uid, period))
        self.currentperiod = period
        if self.currentperiod == 1:
            del self.histo[:]

    def remote_display_decision(self):
        logger.info(u"{} Decision".format(self._le2mclt.uid))
        if self._le2mclt.simulation:
            decision = \
                random.randrange(
                    pms.DECISION_MIN,
                    pms.DECISION_MAX + pms.DECISION_STEP,
                    pms.DECISION_STEP)
            logger.info(u"{} Send back {}".format(self._le2mclt.uid, decision))
            return decision
        else: 
            defered = defer.Deferred()
            ecran_decision = GuiDecision(
                defered, self._le2mclt.automatique,
                self._le2mclt.screen, self.currentperiod, self.histo)
            ecran_decision.show()
            return defered

    def remote_display_summary(self, period_content):
        logger.info(u"{} Summary".format(self._le2mclt.uid))
        if not self.histo:
            headers, self._histo_vars = texts_HM.get_histo()
            self.histo.append(headers)
        self.histo.append([period_content.get(k, "") for k in self._histo_vars])
        if self._le2mclt.simulation:
            return 1
        else:
            defered = defer.Deferred()
            ecran_recap = GuiRecapitulatif(
                defered, self._le2mclt.automatique, self._le2mclt.screen,
                self.currentperiod, self.histo,
                texts_HM.get_text_summary(period_content),
                size_histo=(HISTO_WIDTH, 120))
            ecran_recap.show()
            return defered

    def remote_display_group_composition(self, group_type):
        logger.debug("Group type: {}".format(group_type))
        text = texts_HM.get_text_composition(group_type)
        return self.le2mclt.get_remote("base").remote_display_information(text)

    def remote_display_expectations(self):
        """
        Display the dialog in which the subject enters his/her expectation
        :return:
        """
        logger.debug(u"{} display_expectations".format(self.le2mclt.uid))
        if self.le2mclt.simulation:
            expectation = random.randrange(
            pms.DECISION_MIN, pms.DECISION_MAX + pms.DECISION_STEP,
            pms.DECISION_STEP)
            logger.info(u"{} Send back {}".format(self.le2mclt.uid, expectation))
            return expectation
        else:
            text_expectation = texts_HM.get_text_expectation()
            defered = defer.Deferred()
            screen_expectation = DExpectation(
                defered, self.le2mclt.automatique, self.le2mclt.screen,
                text_expectation)
            screen_expectation.show()
            return defered

