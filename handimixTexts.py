# -*- coding: utf-8 -*-

import os
import configuration.configparam as params
from util.utiltools import get_pluriel
import handimixParams as pms
import gettext
from util.utili18n import le2mtrans

try:
    localedir = os.path.join(params.getp("PARTSDIR"), "Handimix", "locale")
    trans_HM = gettext.translation(
        "Handimix", localedir, languages=[params.getp("LANG")]).ugettext
except (AttributeError, IOError):
    trans_HM = lambda x: x


def get_histo():
    histo = list()
    histo.append((le2mtrans(u"Period"), "HM_period"))
    histo.append((trans_HM(u"Individual\naccount"), "HM_indiv_account"))
    histo.append((trans_HM(u"Group\naccount"), "HM_public_account"))
    histo.append((trans_HM(u"Total in\nthe group\naccount"),
                  "HM_public_account_group"))
    histo.append((trans_HM(u"Payoff\nfrom\nindividual\naccount"),
                  "HM_indivaccountpayoff"))
    histo.append((trans_HM(u"Payoff\nfrom\ngroup\naccount"),
                  "HM_groupaccountpayoff"))
    histo.append((le2mtrans(u"Period\npayoff"), "HM_periodpayoff"))
    histo.append((le2mtrans(u"Cumulative\npayoff"), "HM_cumulativepayoff"))

    return zip(*histo)  # return the_headers, the_vars


def get_text_explanation():
    return trans_HM(u"You have an endowment of {} tokens.").format(pms.DOTATION)


def get_text_label_decision():
    return trans_HM(u"Please enter the number of token(s) you put on the "
                     u"public account")


def get_text_summary(period_content):
    txt = trans_HM(u"You put {} in your individual account and {} in the "
                    u"public account. Your group put {} in the public "
                    u"account.\nYour payoff for the current period is equal "
                    u"to {}.").format(
        get_pluriel(period_content.get("HM_indiv"), trans_HM(u"token")),
        get_pluriel(period_content.get("HM_public"), trans_HM(u"token")),
        get_pluriel(period_content.get("HM_publicgroup"), trans_HM(u"token")),
        get_pluriel(period_content.get("HM_periodpayoff"), pms.MONNAIE))
    return txt

