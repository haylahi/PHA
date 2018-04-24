from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging


class CalculeBestPrice(models.TransientModel):
    _name = "pha.wizard.calcule.best.price"

    filter = fields.Selection([('all',_('All products')),
                               ('category', _('Product Category')),
                               ('product', _('One product')),
                               ('list', _('List of products')),],string="Calculer", required=True,default='all')
    category_id = fields.Many2one('product.category',string='Category')
    product_id = fields.Many2one('product.template', string='Product')
    product_ids = fields.Many2many('product.template', string='Products')
    date_currency_rate = fields.Date('Currency rate Date')


    @api.multi
    def calculate(self):
        product_tmpl=self.env['product.template']
        date = self.date_currency_rate if self.date_currency_rate else None
        if self.filter == 'all' :
            products = product_tmpl.search([('sale_ok','=',True)])
            return products.update_sale_price(date=date)

        if self.filter == 'category' :
            products = product_tmpl.search([('categ_id','=',self.category_id.id)])
            return products.update_sale_price(date=date)

        if self.filter == 'product' :
            return self.product_id.update_sale_price(date=date)

        if self.filter == 'list' :
            return self.product_ids.update_sale_price(date=date)

