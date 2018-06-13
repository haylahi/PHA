from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class TrialBalanceReportWizard(models.TransientModel):
    """Trial balance report wizard."""

    _inherit = "trial.balance.report.wizard"
    
    """
    hide_account_balance_at_0 = fields.Selection([('tous', 'Afficher tout'),
                                                 ('nmvt','Masquer les comptes non mouvementés et soldés'),
                                                 ('soldes', 'Masquer uniquement les comptes non mouvementés')],
                                                string='Comptes soldés',
                                                required=True,
                                                default='tous',
                                                help='test')
    """
    comptes_soldes = fields.Selection([('tous', 'Afficher tout'),
                                         ('nmvt','Masquer les comptes non mouvementés et soldés'),
                                         ('soldes', 'Masquer uniquement les comptes non mouvementés')],
                                        string='Comptes soldés',
                                        required=True,
                                        default='soldes')

    
    masquer_detail_groupes = fields.Boolean("Masquer le détail des groupes")
    
    hierarchy_on = fields.Selection([('computed', 'Computed Accounts'),
                                 ('relation', 'Child Accounts')],
                                string='Hierarchy On',
                                required=True,
                                default='relation')

    
    # Paramètre "Masquer les comptes non mouvementés"
    #masquer_cptes_n_mouvementes = fields.Boolean(string='Masquer les comptes non mouvementés')
    
    # Paramètre "Masquer le détail des groupes"
    

    def _prepare_report_trial_balance(self):
        # on récupère le tableau créé par la classe mère
        export_base = super(TrialBalanceReportWizard, self)._prepare_report_trial_balance()
        _logger.info("\n export_base : " + str(export_base))
        
        _logger.info("\n self.masquer_detail_groupes : " + str(self.masquer_detail_groupes))
        # on ajoute nos deux paramètres
        #export['masquer_cptes_n_mouvementes' : self.masquer_cptes_n_mouvementes]
        export_base['masquer_detail_groupes'] = self.masquer_detail_groupes
        export_base['comptes_soldes'] = self.comptes_soldes
        
        return export_base
    
class TrialBalanceReportCompute(models.TransientModel):

    _inherit = 'report_trial_balance'
    
    def _prepare_report_general_ledger(self, account_ids):

        prepare_base = super(TrialBalanceReportCompute, self)._prepare_report_general_ledger(account_ids) 

        hide_account_balance_at_0 = False
        if self.comptes_soldes == 'nmvt' :
            hide_account_balance_at_0 = True

        prepare_base['hide_account_balance_at_0']  = hide_account_balance_at_0
        
        return prepare_base