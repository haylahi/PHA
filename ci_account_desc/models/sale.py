# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import logging
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_title= fields.Boolean(related='product_id.is_title')

    @api.model
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id.is_title:
            vals = {}
            vals['price_unit'] = 0
            vals['product_uom_qty'] = 1
            self.update(vals)
        return res

    def _update_line_quantity(self, values):
        if self.product_title :
            values['product_uom_qty']=1
        super(SaleOrderLine, self)._update_line_quantity(values)

