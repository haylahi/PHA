# -*- coding: utf-8 -*-

import itertools
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
from odoo.tools import pycompat


class ResPartner(models.Model):
    _inherit = ['res.partner']

    fax = fields.Char(string='Fax')
    tva_migration=fields.Char(string='TVA Migration')
