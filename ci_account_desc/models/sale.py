# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id.is_title:
            vals = {}
            vals['price_unit'] = 0
            vals['product_uom_qty'] = 0
            self.update(vals)
        return res
