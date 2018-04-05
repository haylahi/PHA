# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.template"
    
    
    @api.multi
    def _compute_cost_from_bom(self):
        bom_obj = self.env['mrp.bom']
        for p in self:
            search_bom_product = bom_obj.search([('product_tmpl_id', '=', p.id)], limit=1, order="id desc")
            if search_bom_product:
                cost = 0.0
                for bom in search_bom_product:
                    if bom.bom_line_ids:
                        for line in bom.bom_line_ids:
                            if line.product_id.cost_price_bom > 0.0:
                                product_cost = line.product_id.cost_price_bom
                            else:
                                product_cost = line.product_id.standard_price
                            product_qty = line.product_qty
                            cost += (product_qty/bom.product_qty * product_cost)
                        p.cost_price_bom = cost

    cost_price_bom = fields.Float(
        'Cost Incl. BOM', compute='_compute_cost_from_bom',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user")

class ProductVariant(models.Model):
    _inherit = "product.product"


    @api.multi
    def _compute_cost_from_bom_product(self):
        bom_obj = self.env['mrp.bom']
        for p in self:
            search_bom_product = bom_obj.search([('product_id', '=', p.id)])
            if search_bom_product:
                cost = 0.0
                for bom in search_bom_product:
                    if bom.bom_line_ids:
                        for line in bom.bom_line_ids:
                            if line.product_id.cost_price_bom > 0.0:
                                product_cost = line.product_id.cost_price_bom
                            else:
                                product_cost = line.product_id.standard_price
                            product_qty = line.product_qty
                            cost += (product_qty/bom.product_qty * product_cost)
                        p.cost_price_bom = cost
    #
    # cost_price_bom = fields.Float(
    #     'Cost Incl. BOM', compute='_compute_cost_from_bom_product',
    #     digits=dp.get_precision('Product Price'),
    #     groups="base.group_user")

                       

