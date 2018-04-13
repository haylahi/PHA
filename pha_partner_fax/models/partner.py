# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = ['res.partner']

    fax = fields.Char(string='Fax')
    tva_migration = fields.Char(string='TVA Migration')
    # parc_materials = fields.Text(string='Parc Matériels')
