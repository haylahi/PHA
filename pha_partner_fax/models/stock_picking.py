# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    contact_id = fields.Many2many('res.partner',string='Contact')

