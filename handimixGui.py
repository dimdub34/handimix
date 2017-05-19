# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import logging
from client.cltgui.cltguidialogs import GuiHistorique
from client.cltgui.cltguiwidgets import WExplication, WPeriod, WSpinbox
from util.utili18n import le2mtrans
import handimixParams as pms
import handimixTexts as textes_HM
from handimixTexts import trans_HM


logger = logging.getLogger("le2m")


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique)

        layout = QtGui.QVBoxLayout(self)

        wperiod = WPeriod(period=periode, ecran_historique=self._historique,
                          parent=self)
        layout.addWidget(wperiod)

        wexplanation = WExplication(
            text=textes_HM.get_text_explanation(),
            parent=self, size=(450, 80))
        layout.addWidget(wexplanation)

        self._wdecision = WSpinbox(
            label=textes_HM.get_text_label_decision(),
            minimum=pms.DECISION_MIN, maximum=pms.DECISION_MAX,
            interval=pms.DECISION_STEP, automatique=self._automatique,
            parent=self)
        layout.addWidget(self._wdecision)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.setWindowTitle(trans_HM(u"Decision"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(
                buttons.button(QtGui.QDialogButtonBox.Ok).click)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass
        if not self._automatique:
            confirmation = QtGui.QMessageBox.question(
                self, le2mtrans(u"Confirmation"),
                le2mtrans(u"Do you confirm your choice?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirmation != QtGui.QMessageBox.Yes: 
                return
        decision = self._wdecision.get_value()
        logger.info(u"Decision callback {}".format(decision))
        self.accept()
        self._defered.callback(decision)


class DConfigure(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        form = QtGui.QFormLayout()
        layout.addLayout(form)

        # treatment
        self._combo_treatment = QtGui.QComboBox()
        self._combo_treatment.addItems(
            list(sorted(pms.TREATMENTS_NAMES.viewvalues())))
        self._combo_treatment.setCurrentIndex(pms.TREATMENT)
        form.addRow(QtGui.QLabel(u"Traitement"), self._combo_treatment)

        # nombre de périodes
        self._spin_periods = QtGui.QSpinBox()
        self._spin_periods.setMinimum(0)
        self._spin_periods.setMaximum(100)
        self._spin_periods.setSingleStep(1)
        self._spin_periods.setValue(pms.NOMBRE_PERIODES)
        self._spin_periods.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_periods.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Nombre de périodes"), self._spin_periods)

        # taille groupes
        self._spin_groups = QtGui.QSpinBox()
        self._spin_groups.setMinimum(2)
        self._spin_groups.setMaximum(100)
        self._spin_groups.setSingleStep(1)
        self._spin_groups.setValue(pms.TAILLE_GROUPES)
        self._spin_groups.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_groups.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Taille des groupes"), self._spin_groups)
        
        # Rendement compte individuel
        self._spin_rendement_indiv = QtGui.QDoubleSpinBox()
        self._spin_rendement_indiv.setMinimum(0)
        self._spin_rendement_indiv.setMaximum(100)
        self._spin_rendement_indiv.setDecimals(2)
        self._spin_rendement_indiv.setSingleStep(0.1)
        self._spin_rendement_indiv.setValue(pms.RENDEMENT_INDIV)
        self._spin_rendement_indiv.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_rendement_indiv.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Rendement du compte individuel"),
                    self._spin_rendement_indiv)

        # Rendement compte collectif
        self._spin_rendement_coll = QtGui.QDoubleSpinBox()
        self._spin_rendement_coll.setMinimum(0)
        self._spin_rendement_coll.setMaximum(100)
        self._spin_rendement_coll.setDecimals(2)
        self._spin_rendement_coll.setSingleStep(0.1)
        self._spin_rendement_coll.setValue(pms.RENDEMENT_COLL)
        self._spin_rendement_coll.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_rendement_coll.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Rendement du compte collectif"),
                    self._spin_rendement_coll)
        
        # Taux de conversion
        self._spin_conversion_rate = QtGui.QDoubleSpinBox()
        self._spin_conversion_rate.setMinimum(0)
        self._spin_conversion_rate.setMaximum(100)
        self._spin_conversion_rate.setDecimals(2)
        self._spin_conversion_rate.setSingleStep(0.1)
        self._spin_conversion_rate.setValue(pms.TAUX_CONVERSION)
        self._spin_conversion_rate.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_conversion_rate.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Taux de conversion des ecus en euros"),
                    self._spin_conversion_rate)

        button = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button.accepted.connect(self._accept)
        button.rejected.connect(self.reject)
        layout.addWidget(button)

        self.setWindowTitle(u"Configurer")
        self.adjustSize()
        self.setFixedSize(self.size())

    def _accept(self):
        pms.TREATMENT = self._combo_treatment.currentIndex()
        pms.NOMBRE_PERIODES = self._spin_periods.value()
        pms.TAILLE_GROUPES = self._spin_groups.value()
        pms.RENDEMENT_INDIV = self._spin_rendement_indiv.value()
        pms.RENDEMENT_COLL = self._spin_rendement_coll.value()
        pms.TAUX_CONVERSION = self._spin_conversion_rate.value()
        self.accept()


class DHandi(QtGui.QDialog):
    def __init__(self, le2msrv):
        QtGui.QDialog.__init__(self, le2msrv.gestionnaire_graphique.screen)

        self.le2msrv = le2msrv
        self.players = self.le2msrv.gestionnaire_joueurs.get_players()
        logger.debug("{}".format(self.players))

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        if self.players:
            self.checkbox = list()
            for p in self.players:
                self.checkbox.append(QtGui.QCheckBox(str(p)))
                try:
                    self.checkbox[-1].setChecked(p.handicap)
                except AttributeError:
                    self.checkbox[-1].setChecked(False)
                layout.addWidget(self.checkbox[-1])
        else:
            layout.addWidget(QtGui.QLabel("Aucun joueur"))

        buttonbox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttonbox.rejected.connect(self.reject)
        buttonbox.accepted.connect(self.accept)
        layout.addWidget(buttonbox)

        self.setWindowTitle("Situation handicap")
        self.adjustSize()

    def accept(self):
        if not self.players:
            return super(DHandi, self).reject()
        confirmation = QtGui.QMessageBox.question(
            self, "Confirmation", "Enregistrer?",
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
        if confirmation != QtGui.QMessageBox.Yes:
            return
        for i, p in enumerate(self.players):
            if self.checkbox[i].isChecked():
                p.handicap = True
            else:
                p.handicap = False
        super(DHandi, self).accept()


class DExpectation(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, text, expec_before=None):
        QtGui.QDialog.__init__(self, parent)

        self._defered = defered
        self._automatique = automatique

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        explanation = WExplication(text=text[0])
        layout.addWidget(explanation)

        self._spin_expectation = WSpinbox(
            parent=self, minimum=pms.DECISION_MIN, maximum=pms.DECISION_MAX,
            interval=pms.DECISION_STEP, label=text[1],
            automatique=self._automatique)
        if expec_before is not None:
            self._spin_expectation.spinBox.setValue(expec_before)
        layout.addWidget(self._spin_expectation)

        button = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button.accepted.connect(self._accept)
        layout.addWidget(button)

        self.setWindowTitle(trans_HM(u"Expectation"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(self._accept)
            self._timer.start(7000)

    def reject(self):
        pass

    def _accept(self):
        try:
            self._timer.stop()
        except AttributeError:
            pass
        expectation = self._spin_expectation.get_value()
        if not self._automatique:
            confirm = QtGui.QMessageBox.question(
                self, u"Confirmation", le2mtrans(u"Do you confirm your choice?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirm != QtGui.QMessageBox.Yes:
                return
        logger.info(le2mtrans(u"Send back {}".format(expectation)))
        self.accept()
        self._defered.callback(expectation)
