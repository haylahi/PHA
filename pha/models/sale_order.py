from openerp import models, fields, api
import math

class sale_order(models.Model):
    _inherit = "sale.order"

    @api.one
    def max_line(self,index,max):
        return (int(math.ceil(index / max)) * max)[0]