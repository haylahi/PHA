# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = ['res.partner']

    parc_materials = fields.Text(string='Parc Matériels')
