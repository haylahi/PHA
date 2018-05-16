# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    category_id = fields.Many2many(string='Étiquettes',related='partner_id.category_id',readonly=True)
    name = fields.Char(string='Reference/Description', readonly=False ,states={'draft': [('readonly', False)],'open': [('readonly', False)],'paid': [('readonly', False)]}, index=True, copy=False, help='The name that will be used on account move lines')
    contact_id = fields.Many2one('res.partner', string='Contact')
