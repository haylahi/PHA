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
        return 1

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
        self.highest_price = max(net_prices) if net_prices else 0.0
        self.lowest_price = min(net_prices) if net_prices else 0.0


        if self.highest_price != 0 :
            hp_line = supplier_info_ids.search([('net_price','=',self.highest_price)])
            hp_line.write({'state_highest_price': True})

        if self.lowest_price != 0 :
            lp_line = supplier_info_ids.search([('net_price','=',self.lowest_price)])
            lp_line.write({'state_lowest_price': True})

        return self.highest_price

    @api.multi
    def update_sale_price(self):
        price_scale = self.env['price.scale'].search([('state','=','open')])

        coef = price_scale[0].get_coef(self.highest_price) if price_scale else 1

        self.list_price = coef * self.highest_price

