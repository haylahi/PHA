from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delai = fields.Char('Délai')

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Datetime(related='order_id.date_order', string='Date')
    zip_partner = fields.Char(related='order_id.partner_id.zip', string='Département', store=True)
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        self.name = str(self.name).split('] ')[-1]

        return result