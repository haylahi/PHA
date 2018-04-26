# -*- coding: utf-8 -*-
from openerp import models, fields, api
import logging


class sale_order_line(models.Model):
    _inherit = "sale.order.line"



    sale_product_ref = fields.Many2one("sale.product.ref")


    @api.onchange('sale_product_ref')
    def onchange_prd_ref(self):
        self.price_unit = self.sale_product_ref.price
        self.name=  "["+str(self.sale_product_ref.ref)+"] "+str(self.name).split('] ')[-1]

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.sale_product_ref = False