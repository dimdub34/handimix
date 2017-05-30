# -*- coding: utf-8 -*-

# variables
WITHOUT_HAND = 0
WITH_HAND = 1
TREATMENTS_NAMES = {WITHOUT_HAND: "Without_hand", WITH_HAND: "With_hand"}

# parameters
TREATMENT = WITHOUT_HAND
NB_HANDICAP = 0
DOTATION = 20
RENDEMENT_INDIV = 1
RENDEMENT_COLL = 0.5
TAUX_CONVERSION = 0.07  # 15 ecus = 1 euro (arrondi supérieur)
NOMBRE_PERIODES = 10
TAILLE_GROUPES = 4
MONNAIE = u"ecu"
EXPECTATION = True

# DECISION
DECISION_MIN = 0
DECISION_MAX = DOTATION
DECISION_STEP = 1


def get_payoff_expectation(expectation, average_others):
    if abs(expectation - round(average_others, 0)) <= 1:
        return 1
    else:
        return 0


