# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    category_id = fields.Many2many(string='Étiquettes',related='partner_id.category_id',readonly=True)

class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    category_id = fields.Many2many(string='Étiquettes',related='partner_id.category_id',readonly=True)
