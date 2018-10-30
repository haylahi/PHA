from odoo import models, fields, api
import logging

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one('res.partner', string='Partenaire', compute='_get_partner', store=True)
    picking_type_id = fields.Many2one(related='picking_id.picking_type_id', store=True)

    @api.depends('state')
    def _get_partner(self):
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                rec.partner_id = rec.move_id.sale_line_id.order_id.partner_id.id

            if rec.picking_type_id.code == 'incoming':
                rec.partner_id = rec.move_id.purchase_line_id.order_id.partner_id.id