# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    product_title = fields.Boolean(related='product_id.is_title')

    @api.model
    def create(self, vals):
        res = super(AccountInvoiceLine, self).create(vals)

        if res.product_id.is_title:
            res.write({'price_unit': 0,'quantity': 0})
        return res
