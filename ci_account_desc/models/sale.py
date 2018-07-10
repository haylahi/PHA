# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import logging


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_title= fields.Boolean(related='product_id.is_title')

    @api.model
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id.is_title:
            vals = {'price_unit':0,
                    'product_uom_qty':1}
            self.update(vals)
        return res

    #
    # @api.multi
    # def _action_launch_procurement_rule(self):
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_move', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     errors = []
    #     for line in self:
    #         if line.state != 'sale' or not line.product_id.type in ('consu','product','service'):
    #             continue
    #         qty = 0.0
    #         for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
    #             qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
    #
    #         logging.info('####float_compare : %s ', float_compare(qty, line.product_uom_qty, precision_digits=precision) )
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0 and  line.product_id.type != 'service':
    #             continue
    #
    #         group_id = line.order_id.procurement_group_id
    #         if not group_id:
    #             group_id = self.env['procurement.group'].create({
    #                 'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
    #                 'sale_id': line.order_id.id,
    #                 'partner_id': line.order_id.partner_shipping_id.id,
    #             })
    #             line.order_id.procurement_group_id = group_id
    #         else:
    #             # In case the procurement group is already created and the order was
    #             # cancelled, we need to update certain values of the group.
    #             updated_vals = {}
    #             if group_id.partner_id != line.order_id.partner_shipping_id:
    #                 updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #             if group_id.move_type != line.order_id.picking_policy:
    #                 updated_vals.update({'move_type': line.order_id.picking_policy})
    #             if updated_vals:
    #                 group_id.write(updated_vals)
    #
    #         values = line._prepare_procurement_values(group_id=group_id)
    #         product_qty = line.product_uom_qty - qty
    #
    #         procurement_uom = line.product_uom
    #         quant_uom = line.product_id.uom_id
    #         get_param = self.env['ir.config_parameter'].sudo().get_param
    #         if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
    #             product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
    #             procurement_uom = quant_uom
    #
    #         try:
    #             self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
    #         except UserError as error:
    #             errors.append(error.name)
    #     if errors:
    #         raise UserError('\n'.join(errors))
    #     return True