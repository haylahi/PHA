# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'
    product_title = fields.Boolean(related='product_id.is_title')