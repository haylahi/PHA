# -*- coding: utf-8 -*-
from openerp import models, fields, api
import logging


class MRPRepairLine(models.Model):
    _inherit = "mrp.repair.line"

    product_tmpl_id = fields.Many2one(related="product_id.product_tmpl_id")
    sale_product_ref = fields.Many2one("sale.product.ref")


    @api.onchange('sale_product_ref')
    def onchange_prd_ref(self):
        if self.sale_product_ref:
            self.price_unit = self.sale_product_ref.price
            self.name =  "["+str(self.sale_product_ref.ref)+"] "+str(self.name).split('] ')[-1]
        else:
            self.onchange_product_id()

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(MRPRepairLine, self).onchange_product_id()
        self.sale_product_ref = False


# class MRPRepairLine(models.Model):
#     _inherit = "mrp.repair.fee"
# 
#     product_tmpl_id = fields.Many2one(related="product_id.product_tmpl_id")
#     sale_product_ref = fields.Many2one("sale.product.ref")
# 
# 
#     @api.onchange('sale_product_ref')
#     def onchange_prd_ref(self):
#         self.price_unit = self.sale_product_ref.price
#         self.name=  "["+str(self.sale_product_ref.ref)+"] "+str(self.name).split('] ')[-1]
# 
#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         self.sale_product_ref = False

