# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, _


class Repair(models.Model):
    _inherit = 'mrp.repair'

    client_ref = fields.Char(string='Customer Reference')


