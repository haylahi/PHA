# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_title_change(self):
        logging.info('-------------- %s', self.product_id)
        if self.product_id.is_title:
            vals = {}
            vals['price_unit'] = 0
            vals['product_uom_qty'] = 0
            self.write(vals)
        # return True
