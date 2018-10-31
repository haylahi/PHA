from odoo import models, fields, api
import logging

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    origin = fields.Char('Origine', compute='_get_origin', store=True)
    s_order_id = fields.Many2one('sale.order', compute='_get_origin', store=True)
    p_order_id = fields.Many2one('purchase.order', compute='_get_origin', store=True)
    partner_id = fields.Many2one('res.partner', string='Partenaire', compute='_get_origin', store=True)
    picking_type_id = fields.Many2one(related='picking_id.picking_type_id', store=True)


    @api.depends('state')
    def _get_origin(self):
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                order_origin = rec.move_id.sale_line_id.order_id
                rec.s_order_id = order_origin.id
                rec.partner_id = order_origin.partner_id.id
                rec.origin = order_origin.name

            if rec.picking_type_id.code == 'incoming':
                order_origin = rec.move_id.purchase_line_id.order_id
                rec.p_order_id = order_origin.id
                rec.partner_id = order_origin.partner_id.id
                rec.origin = order_origin.name