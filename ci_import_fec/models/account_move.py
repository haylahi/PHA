# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fec_reconcile_mapping = fields.Char(string='Reconcile code')
    is_reconcile_mapping = fields.Boolean(string="Reconciled")
