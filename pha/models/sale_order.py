from odoo import models, fields, api
import math

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    def max_line(self,index,max):
        max_line = int(math.ceil(index / max)) * max
        return max_line