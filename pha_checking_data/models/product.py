# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_verified = fields.Boolean('Verified', default=False)

    @api.multi
    def check_object(self):
        self.ensure_one()
        if self.is_verified:
            self.is_verified = False
        else:
            self.is_verified = True
        return True
