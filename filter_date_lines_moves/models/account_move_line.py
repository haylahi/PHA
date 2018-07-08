# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)

from datetime import datetime


class account_move_line(models.Model):
    _inherit = "account.move.line"
    
    #date_month = fields.Char(string='Date Month',compute='_get_date_month',readonly=True)
    date_month = fields.Selection([
        (1,'Janvier'),
        (2,'F\xe9vrier'),
        (3,'Mars'),
        (4,'Avril'),
        (5,'Mai'),
        (6,'Juin'),
        (7,'Juillet'),
        (8,'Ao\xfbt'),
        (9,'Septembre'),
        (10,'Octobre'),
        (11,'Novembre'),
        (12,'D\xe9cembre')], string='Mois', compute='_get_date_month', readonly=True, store=True)
    
    #date_year= fields.Selection([(a,str(a)) for a in range(datetime.now().year-10,datetime.now().year+1)],string='Année', compute='_get_date_year', readonly=True, store=True)
    date_year = fields.Integer(string='Année', compute='_get_date_year', readonly=True, store=True)
    
    
    @api.one
    @api.depends('date')
    def _get_date_month(self):
 
        current_date = datetime.strptime(str(self.date),'%Y-%m-%d')
        mois = current_date.date().month
        
        # _logger.info("\n\n mois : "+ str(mois))

        self.date_month = mois
        
    @api.one
    @api.depends('date')
    def _get_date_year(self):
 
        current_date = datetime.strptime(str(self.date),'%Y-%m-%d')
        year = current_date.date().year
        
        # _logger.info("\n\n mois : "+ str(year))

        self.date_year = year
        
    
