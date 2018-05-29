# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons import decimal_precision as dp

from odoo.tools import pycompat


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        super(PricelistItem, self)._get_pricelist_item_name_price()
        if self.product_tmpl_id:
            self.name = self.product_tmpl_id.display_name



