# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from openerp import api, fields, models, _
from openerp import tools
import logging
from openerp.exceptions import ValidationError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def compute_discounted_pack_price(self):
        for product in self:
            product.has_discounted_amount = False
            if product.is_pack:
                price = 0
                for prod in product.wk_product_pack:
                    price = price + prod.product_name.lst_price * prod.product_quantity
                rem_price = price - product.lst_price
                product.pack_products_price = price
                if rem_price <= 0:
                    product.has_discounted_amount = True

    is_pack = fields.Boolean(
        string='Is product pack')
    wk_product_pack = fields.One2many(
        comodel_name='product.pack', 
        inverse_name='wk_product_template', 
        string='Product pack', copy=True)
    pack_stock_management = fields.Selection(
        [('decrmnt_pack', 'Decrement Pack Only'),
        ('decrmnt_products', 'Decrement Products Only'),
        ('decrmnt_both', 'Decrement Both')], 
        string='Pack Stock Management', 
        default='decrmnt_products')

    has_discounted_amount = fields.Boolean(
        compute="compute_discounted_pack_price",
        string="Remaning price")
    pack_products_price = fields.Float(
        compute="compute_discounted_pack_price",
        string="Total Product Price")

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        pk_dec = self.pack_stock_management
        if pk_dec == 'decrmnt_products':
            prd_type = 'service'
        elif pk_dec == 'decrmnt_both':
            prd_type = 'product'
        else:
            prd_type = 'consu'
        self.type = prd_type

    @api.model
    def create(self, vals):
        if vals.get('is_pack'):
            if not vals.get('wk_product_pack'):
                raise ValidationError(
                    'No products in this pack. Select atleast one product.')
        return super(ProductTemplate, self).create(vals)

    @api.onchange('type')
    def select_default_pack_mgmnt_onchange_type(self):
        if self.is_pack:
            prd_type = self.type
            if prd_type == 'service':
                pack_type = 'decrmnt_products'
            elif prd_type == 'product':
                pack_type = 'decrmnt_both'
            else:
                pack_type = 'decrmnt_pack'
            self.pack_stock_management = pack_type


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        pk_dec = self.pack_stock_management
        if pk_dec == 'decrmnt_products':
            prd_type = 'service'
        elif pk_dec == 'decrmnt_both':
            prd_type = 'product'
        else:
            prd_type = 'consu'
        self.type = prd_type


class ProductPack(models.Model):
    _name = 'product.pack'

    product_name = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    product_quantity = fields.Integer(
        string='Quantity', required=True, default=1)
    wk_product_template = fields.Many2one(
        comodel_name='product.template', string='Product pack')
    wk_image = fields.Binary(
        related='product_name.image_medium', string='Image', store=True)
    price = fields.Float(related='product_name.lst_price',
                         string='Product Price')
    uom_id = fields.Many2one(
        related='product_name.uom_id', string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_name.name', readonly="1")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

   
    @api.multi
    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_move', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        for line in self:
            if line.product_id.is_pack:
                qty = 0.0
                for move in line.move_ids:
                    qty += move.product_qty
                if not line.order_id.procurement_group_id:
                    line.order_id.procurement_group_id = self.env['procurement.group'].create({
                        'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)

                if line.product_id.pack_stock_management == 'decrmnt_both':
                    product_qty = line.product_uom_qty - qty
                    try:
                        res = self.env['procurement.group'].run(line.product_id, product_qty, line.product_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                    except UserError as error:
                        errors.append(error.name)

                if line.product_id.pack_stock_management != 'decrmnt_pack':
                    for pack_obj in line.product_id.wk_product_pack:
                        product_qty = line.product_uom_qty * pack_obj.product_quantity
                        try:
                            res = self.env['procurement.group'].run(pack_obj.product_name, product_qty, line.product_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                        except UserError as error:
                            errors.append(error.name)
        return super(SaleOrderLine, self)._action_launch_procurement_rule()

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        res = super(SaleOrderLine,self)._onchange_product_id_check_availability()
        product_obj = self.product_id
        if self.product_id.type == 'product':
            if product_obj.is_pack:
                warning_mess = {}
                for pack_product in product_obj.wk_product_pack:
                    qty = self.product_uom_qty
                    _logger.info("#################%r", qty)
                    if qty * pack_product.product_quantity > pack_product.product_name.virtual_available:
                        warning_mess = {
                            'title': _('Not enough inventory!'),
                            'message': ('You plan to sell %s quantities of the pack %s but you have only  %s quantities of the product %s available, and the total quantity to sell is  %s !!' % (qty, pack_product.product_name.name, pack_product.product_name.virtual_available, pack_product.product_name.name, qty * pack_product.product_quantity))
                        }
                        return {'warning': warning_mess}
            return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
