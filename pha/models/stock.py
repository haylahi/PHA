from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one(related='move_id.sale_line_id.order_id.partner_id', store=True)
    picking_type_id = fields.Many2one(related='picking_id.picking_type_id', store=True)