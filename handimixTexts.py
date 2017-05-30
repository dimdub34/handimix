# -*- coding: utf-8 -*-

import os
import logging
import configuration.configparam as params
from util.utiltools import get_pluriel
import handimixParams as pms
import gettext
from util.utili18n import le2mtrans

logger = logging.getLogger("le2m")

try:
    localedir = os.path.join(params.getp("PARTSDIR"), "handimix", "locale")
    trans_HM = gettext.translation(
        "handimix", localedir, languages=[params.getp("LANG")]).ugettext
except (AttributeError, IOError):
    logger.warning("Fichier de traduction non trouvé")
    trans_HM = lambda x: x


def get_histo():
    histo = list()
    histo.append((le2mtrans(u"Period"), "HM_period"))
    histo.append((trans_HM(u"Individual\naccount"), "HM_indiv_account"))
    histo.append((trans_HM(u"Group\naccount"), "HM_public_account"))
    histo.append((trans_HM(u"Total in\nthe group\naccount"),
                  "HM_public_account_group"))
    histo.append((trans_HM(u"Payoff\nfrom\nindividual\naccount"),
                  "HM_payoff_from_indiv_account"))
    histo.append((trans_HM(u"Payoff\nfrom\ngroup\naccount"),
                  "HM_payoff_from_public_account"))
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
        get_pluriel(period_content.get("HM_indiv_account"), trans_HM(u"token")),
        get_pluriel(period_content.get("HM_public_account"), trans_HM(u"token")),
        get_pluriel(period_content.get("HM_public_account_group"), trans_HM(u"token")),
        get_pluriel(period_content.get("HM_periodpayoff"), pms.MONNAIE))
    return txt


def get_text_expectation():
    text = (trans_HM(u"How much token(s) do you think the other members "
               u"of your group will put, on average, in the collective "
               u"account?"), trans_HM(u"Your expectation"))
    return text


def get_text_composition(group_type):
    text = trans_HM(u"There are {} people with a handicap, each one is in a "
                    u"separate group.").format(pms.NB_HANDICAP) + u" "
    if group_type == pms.WITHOUT_HAND:
        text += trans_HM(u"There is no people with a handicap in your group.")
    else:
        text += trans_HM(u"There is one people with a handicap in your group.")
    return text


def get_text_help():
    text = u"<!DOCTYPE html>" \
           u"<html>" \
           u"<head>" \
           u"<meta charset='utf-8' />" \
           u"</head>" \
           u"<body>" \
           u"<h1>Aide</h1>" \
           u"<h2>Avant de lancer la partie</h2>" \
           u"<ul>" \
           u"<li>Configurer la partie (traitement etc.) en cliquant sur le " \
           u"menu 'Configurer'<li>" \
           u"<li>Si traitement WITHOUT_HAND, rien d'autre à faire</li>" \
           u"<li>Si <strong><span style='color:brown;'>traitement WITH_HAND</span></strong>" \
           u"<ul>" \
           u"<li><strong>Fixer l'emplacement des personnes à validité réduite</strong> avec le " \
           u"menu Set Hand. (cocher les postes correspondants)</li>" \
           u"<li><strong>Former manuellement les groupes</strong>, en cliquant sur le sous-menu " \
           u"'Editer les groupes' du menu Options: saisir la taille des groupes puis " \
           u"cliquer sur 'Former les groupes'. Vérifier ensuite la composition " \
           u"des groupes, pour ce qui concerne les personnes à validité réduite." \
           u" Si la composition des groupes est ok, cliquer sur 'Enregistrer'. " \
           u"Si elle n'est pas ok, changer les groupes des personnes avec " \
           u"les menus déroulants à disposition. Quand c'est ok, cliquer sur " \
           u"enregistrer.</li>" \
           u"</ul>" \
           u"</ul>" \
           u"<h2>Lancement de la partie</h2>" \
           u"Cliquer sur le menu 'Démarrer'" \
           u"<h2>Lorsque la partie est terminée</h2>" \
           u"<ul>" \
           u"<li>Cliquer sur le menu 'Afficher les gains', puis dans la fenêtre, " \
           u"sur le bouton 'Ajouter au gains finaux'. Fermer la fenêtre.</li>" \
           u"<li>Dans le menu 'Expérience', cliquer sur le sous-menu 'Gains', " \
           u"puis dans la fenêtre ouverte, cliquer sur 'Imprimer', puis sur " \
           u"'Afficher sur les postes'. Cela affiche l'écran final sur les postes " \
           u"clients, avec leur gain à l'expérience puis une zone pour écrire " \
           u"des commentaires.</li>" \
           u"<li>Appeler les sujets un par un par leur identifiant de poste " \
           u"pour les rémunérer</li>" \
           u"</ul>" \
           u"</body>" \
           u"</html>"
    return text