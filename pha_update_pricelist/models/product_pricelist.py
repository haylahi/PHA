# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class PriceList(models.Model):
    _inherit="product.pricelist"

    automatic_update = fields.Boolean("mise à jour automatique", default=True)


