# -*- coding: utf-8 -*-
from openerp import models, fields
import logging


class sale_product_ref(models.Model):
    _name = "sale.product.ref"
    _rec_name = "ref"

    sequence = fields.Integer('sequence',
                              help="Sequence for the handle.")

    ref = fields.Char(string="reference",
                      required=True)

    label = fields.Char(string="label",
                        required=True)

    price = fields.Float(string="price",
                         required=True)

    product_id = fields.Many2one("product.template", ondelete="cascade")

    _sql_constraints = [
        ('ref_unique',
         'unique(ref)',
         'Choose another value Reference has to be unique!')
    ]


class product_template(models.Model):
    _inherit = "product.template"

    product_ref_list = fields.One2many("sale.product.ref", "product_id",
                                       string="product refs")
