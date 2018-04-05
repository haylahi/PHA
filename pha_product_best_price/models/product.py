# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO, StringIO
import datetime
import logging
from odoo.tools import pycompat

class ProductSupplierinfor(models.Model):
    """ Product Supplier info to add net price. """

    _inherit = ['product.supplierinfo']

    state_lowest_price = fields.Boolean("Lowest ", default=False)
    state_highest_price = fields.Boolean("Highest ", default=False)
    net_price= fields.Float(compute='_compute_net_price',string="Prix Net",store=True)
    @api.one
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

    highest_price = fields.Float(compute='_compute_highest_price', string="Highest Price")
    lowest_price = fields.Float(compute='_compute_highest_price', string="Lowest Price")

    @api.multi
    def _compute_highest_price(self):
        supplier_info_ids =self.seller_ids

        # '''set all states to false'''
        supplier_info_ids.write({'state_lowest_price' : False,
                                 'state_highest_price': False,})
        net_prices = self.seller_ids.mapped('net_price')
        highest_price = max(net_prices) if net_prices else 0.0
        lowest_price = min(net_prices) if net_prices else 0.0

        default_currency = self.env.user.company_id.currency_id
        if highest_price != 0 :
            hp_line = supplier_info_ids.search([('id','in',supplier_info_ids.ids),('net_price','=',highest_price)])[0]
            if hp_line.currency_id.id != default_currency.id:
                highest_price = highest_price / hp_line.currency_id.rate
            hp_line.write({'state_highest_price': True})

        if lowest_price != 0 :
            lp_line = supplier_info_ids.search([('id','in',supplier_info_ids.ids),('net_price','=',lowest_price)])[0]
            if lp_line.currency_id.id != default_currency.id:
                lowest_price = lowest_price / lp_line.currency_id.rate
            lp_line.write({'state_lowest_price': True})

        self.highest_price = highest_price
        self.lowest_price = lowest_price

        return self.highest_price

    @api.multi
    def update_sale_price(self):
        for rec in self:
            logging.info('test : %s' % rec)
            logging.info('test : %s' % rec[0].highest_price)
            rec= rec[0]
            logging.info('test : %s' % rec.highest_price)
            price_scale = self.env['price.scale'].search([('state','=','open')])
            coef = price_scale[0].get_coef(rec.highest_price)
            rec.list_price = coef * rec.highest_price
            rec.standard_price = rec.lowest_price

    @api.multi
    def update_all(self):
        self.ensure_one()
        self.update_sale_price()
