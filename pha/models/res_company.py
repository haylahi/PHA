from odoo import models, fields, api

class Company(models.Model):
    _inherit = "res.company"

    external_report_layout = fields.Selection(selection_add=[('pha', 'PHA')])