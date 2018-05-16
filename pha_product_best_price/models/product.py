# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO, StringIO
import datetime
import logging
from odoo.tools import pycompat
import odoo.addons.decimal_precision as dp

class ProductSupplierinfor(models.Model):
    """ Product Supplier info to add net price. """

    _inherit = ['product.supplierinfo']
    state_lowest_price = fields.Boolean("Lowest ", default=False)
    state_highest_price = fields.Boolean("Highest ", default=False)
    net_price= fields.Float(compute='_compute_net_price',string="Prix Net",store=True, digits=dp.get_precision('Product Price'))
    @api.multi
    @api.depends('price','discount')
    def _compute_net_price(self):
        for record in self:
            record.net_price = record.price -(record.price * record.discount)/100.0



class PriceScaleLine(models.Model):
    """ Product Scale lines for price evaluating. """
    _name = 'price.scale.line'

    name = fields.Char(string='name')
    min_price=fields.Float('Minimal Price', default=0.0)
    max_price=fields.Float('Maximal Price', default=0.0)
    coef =fields.Float('Coefficient Applicable', default=0.0)
    scale_id = fields.Many2one('price.scale', string="scale")

class PriceScale(models.Model):
    """ Product Scale for price evaluating. """
    _name = 'price.scale'

    name=fields.Char(string='name')
    state = fields.Selection(selection=[('open', 'open'),
                                        ('close', 'close'),
                                        ], default='close')

    price_scale_line_ids=fields.One2many('price.scale.line','scale_id',string="scale lines")


    @api.multi
    def get_coef(self,price):
        if price:
            scale_line = self.price_scale_line_ids.search([('min_price','<=',price),
                                                      ('max_price', '>=', price)])
            if scale_line:
                return scale_line.coef

        #TODO: rendre le coef standar parametrable, le 1.68 est specific pour le projet pha
        return  1.68



class ProductTemplate(models.Model):
    _inherit = ['product.template']

    highest_price = fields.Float(string="Highest Price")
    lowest_price = fields.Float(string="Lowest Price")
    partner_id_low_price = fields.Many2one('res.partner', string='Fournisseur ppb', help="Fournisseur proposant le prix le plus bas.")
    partner_id_high_price = fields.Many2one('res.partner', string='Fournisseur ppe', help="Fournisseur proposant le prix le plus élevé.")

    @api.multi
    def compute_highest_price(self, date=None):
        for rec in self :
            supplier_info_ids = rec.seller_ids
            default_currency = rec.env.user.company_id.currency_id

            # '''set all states to false'''
            supplier_info_ids.write({'state_lowest_price' : False,
                                     'state_highest_price': False,})
            partner_id_high_price = partner_id_low_price = False

            net_prices = supplier_info_ids.mapped('net_price')
            highest_price = max(net_prices) if net_prices else 0.0
            lowest_price = min(net_prices) if net_prices else 0.0


            if highest_price != 0 :
                hp_line = supplier_info_ids.search([('id','in',supplier_info_ids.ids),('net_price','=',highest_price)])
                partner_id_high_price = hp_line[0].name.id
                highest_price = self.process_supplier_line_rate(price=highest_price,line=hp_line[0],default_currency=default_currency,date=date)
                hp_line.write({'state_highest_price': True})

            if lowest_price != 0 :
                lp_line = supplier_info_ids.search([('id','in',supplier_info_ids.ids),('net_price','=',lowest_price)])
                partner_id_low_price = lp_line[0].name.id
                lowest_price = self.process_supplier_line_rate(price=lowest_price,line=lp_line[0],default_currency=default_currency,date=date)
                lp_line.write({'state_lowest_price': True})

            rec.write({'highest_price': highest_price,
                       'partner_id_high_price':partner_id_high_price,
                       'lowest_price': lowest_price,
                       'partner_id_low_price': partner_id_low_price,})

    def process_supplier_line_rate(self, price, line, default_currency, date=None):
        if len(line) != 0 and line.currency_id.id != default_currency.id:
            if date:
                rate = self.env['res.currency.rate'].search([('currency_id', '=', line.currency_id.id),('name', '=', date)])
                rate = rate.rate if rate else line.currency_id.rate
                return price / rate
        return price / line.currency_id.rate

    @api.multi
    def update_sale_price(self, context={}, date=None):
        price_scale = self.env['price.scale'].search([('state', '=', 'open')])
        for rec in self:
            rec = rec[0]
            rec.compute_highest_price(date=date)

            #FIXME: valeur en hard ici, spécifique pour pha pour ignorer le calcule des produits déstockable
            if rec.categ_id.name != 'Déstockable':
                highest_price = rec.highest_price
                coef = price_scale[0].get_coef(highest_price)
                list_price = coef * highest_price
                standard_price = rec['lowest_price']
                rec.write({'list_price':list_price,'standard_price':standard_price})