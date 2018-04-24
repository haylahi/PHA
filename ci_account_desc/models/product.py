# -*- coding: utf-8 -*-

import itertools
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_title = fields.Boolean("Title", default=False)
    description_title = fields.Text(string="Tiltle Description")
