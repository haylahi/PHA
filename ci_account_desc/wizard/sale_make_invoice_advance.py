# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @staticmethod
    def change_product_line_price(line_ids, value):
        for line in line_ids:
            line.write({'price_unit': value})
            line.write({'product_uom_qty': value})

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        line_ids = sale_orders.mapped('order_line').filtered(lambda m: m.product_id.is_title)

        self.change_product_line_price(line_ids, 1)
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        self.change_product_line_price(line_ids, 0)

        return res
