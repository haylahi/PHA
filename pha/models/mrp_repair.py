# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare



class Repair(models.Model):
    _inherit = 'mrp.repair'

    client_ref = fields.Char(string='Customer Reference')


