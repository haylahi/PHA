# -*- coding: utf-8 -*-
# © 2017-2018 CADR'IN SITU (http://www.cadrinsitu.com/)
# @author: Tarik ARAB <tarik.arab@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fec_reconcile_mapping = fields.Char(string='Reconcile code')
    is_reconcile_mapping = fields.Boolean(string="Reconciled")
