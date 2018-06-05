# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class TrialBalanceReport(models.TransientModel):
    
    _inherit = 'report_trial_balance'
    
    #hide_account_balance_at_0 = fields.Selection([('tous', 'Afficher tout'),('nmvt','Masquer les comptes non mouvementés et soldés'),('soldes', 'Masquer uniquement les comptes non mouvementés')], default='nmvt', string= 'Comptes soldés', required=True)
    comptes_soldes = fields.Selection([('tous', 'Afficher tout'),
                                         ('nmvt','Masquer les comptes non mouvementés et soldés'),
                                         ('soldes', 'Masquer uniquement les comptes non mouvementés')],
                                        string='Comptes soldés',
                                        required=True,
                                        default='tous')
    
    # le calcul automatique sur le total des groupes théoriques ne nous intéresse pas, on garde seulement le calcul concret de la somme des comptes appartenant réellement au groupe
    hierarchy_on = fields.Selection([('relation', 'Child Accounts')
                                     , ('computed', 'Computed Accounts'),],
                                string='Hierarchy On',
                                required=True,
                                default='relation')
    
    # Paramètre "Masquer les comptes non mouvementés"
    #masquer_cptes_n_mouvementes = fields.Boolean()
    
    # Paramètre "Masquer le détail des groupes"
    masquer_detail_groupes = fields.Boolean()
    
    def _inject_account_values(self, account_ids):
        """Inject report values for report_trial_balance_account"""
        
        query_inject_account = """
INSERT INTO
    report_trial_balance_account
    (
    report_id,
    create_uid,
    create_date,
    account_id,
    parent_id,
    code,
    name,
    initial_balance,
    debit,
    credit,
    final_balance
    )
SELECT
    %s AS report_id,
    %s AS create_uid,
    NOW() AS create_date,
    acc.id,
    acc.group_id,
    acc.code,
    acc.name,
    coalesce(rag.initial_balance, 0) AS initial_balance,
    coalesce(rag.final_debit - rag.initial_debit, 0) AS debit,
    coalesce(rag.final_credit - rag.initial_credit, 0) AS credit,
    coalesce(rag.final_balance, 0) AS final_balance
FROM
    account_account acc
    LEFT OUTER JOIN report_general_ledger_account AS rag
        ON rag.account_id = acc.id AND rag.report_id = %s
WHERE
    acc.id in %s
        """
        
        # on affiche ni les comptes non mouvementés ni les comptes soldés
        if self.comptes_soldes == 'nmvt':
            query_inject_account += """ AND final_balance IS NOT NULL AND final_balance != 0"""
            
        # on masque uniquement les comptes non mouvementés    
        elif self.comptes_soldes == 'soldes':
            query_inject_account += """ AND (coalesce(rag.final_debit - rag.initial_debit, 0) !=0 OR coalesce(rag.final_credit - rag.initial_credit, 0) !=0)"""
        _logger.info("\n self.comptes_soldes : " + str(self.comptes_soldes)) 
        _logger.info("\n query_inject_account : " + str(query_inject_account))   
        
            
        query_inject_account_params = (
            self.id,
            self.env.uid,
            self.general_ledger_id.id,
            account_ids._ids,
        )
        self.env.cr.execute(query_inject_account, query_inject_account_params)
    
    
    def _delete_detail_group(self):
        
        query_inject_account = """
                DELETE FROM report_trial_balance_account
                WHERE parent_id is not null
                AND report_id = %s
                        """
         
        query_inject_account_params = (
            self.id,
        )               
        self.env.cr.execute(query_inject_account, query_inject_account_params)
        
    def _delete_groupes_balance_0(self):
        
        # on supprime les groupes non mouvementés et soldés
        if self.comptes_soldes == 'nmvt' :
            
            query_inject_account = """
                    DELETE FROM report_trial_balance_account
                    WHERE account_group_id is not null 
                    AND (final_balance IS NULL OR final_balance = 0)
                    AND report_id = %s
                            """
        # on supprime uniquement les groupes non mouvementés                   
        if self.comptes_soldes == 'soldes' :
            
            query_inject_account = """
                    DELETE FROM report_trial_balance_account
                    WHERE account_group_id is not null 
                    AND (coalesce(debit, 0) =0 AND coalesce(credit, 0) =0)
                    AND report_id = %s
                            """
         
        query_inject_account_params = (
            self.id,
        )               
        self.env.cr.execute(query_inject_account, query_inject_account_params)
        
    
        
    
class TrialBalanceReportAccount(models.TransientModel):
    _inherit = 'report_trial_balance_account'
    # on supprime l'apparition des groupes en premier sur le rapport
    _order = 'level, name'
    
    # tri personnalisé
    def _generate_order_by(self, order_spec, query):
        my_order = "SUBSTRING(code,0,4) ASC, level,code, name"            
        if order_spec:
            return my_order + ', ' + super(sale_order, self)._generate_order_by(order_spec, query)
        return " order by " + my_order
    

class TrialBalanceReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_trial_balance'
    
                            
    @api.multi
    def compute_data_for_report(self):
        
        super(TrialBalanceReportCompute, self).compute_data_for_report() 
        
        if self.masquer_detail_groupes == True :
            self._delete_detail_group()
            
        if self.comptes_soldes == 'nmvt' or self.comptes_soldes == 'soldes' :
            self._delete_groupes_balance_0()
    

      
