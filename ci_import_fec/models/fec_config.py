# -*- coding: utf-8 -*-
# © 2017-2018 CADR'IN SITU (http://www.cadrinsitu.com/)
# @author: Tarik ARAB <tarik.arab@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools, _


class ImportFECConfig(models.Model):
    _name = "ci.account.import.fec.config"

    name = fields.Char('Nom', compute="_get_name")
    country_id = fields.Many2one('res.country', string="Localisation")
    start_code = fields.Integer(string="Starting code")
    end_code = fields.Integer(string="Ending code")
    user_type_id = fields.Many2one('account.account.type', string="Type")
    reconcile = fields.Boolean('Autoriser le lettrage')

    @api.multi
    def _get_name(self):
        for obj in self:
            if obj.start_code and obj.end_code:
                obj.name = "[ %s - %s ]" % (obj.start_code, obj.end_code)
            else:
                obj.name = "/"
