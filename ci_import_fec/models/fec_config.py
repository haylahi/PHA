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
    # encoded_start_code = fields.Integer(string="Encoded Starting code", compute="_get_encoded_sc", store=True)
    # encoded_end_code = fields.Integer(string="Encoded Ending code", compute="_get_encoded_ec", store=True)
    user_type_id = fields.Many2one('account.account.type', string="Type")
    reconcile = fields.Boolean('Autoriser le lettrage')

    @api.multi
    def _get_name(self):
        for obj in self:
            if obj.start_code and obj.end_code:
                obj.name = "[ %s - %s ]" % (obj.start_code, obj.end_code)
            else:
                obj.name = "/"

    # @api.multi
    # @api.depends('start_code')
    # def _get_encoded_sc(self):
    #     for obj in self:
    #         if len(str(obj.start_code)) < 10:
    #             len_code = 10 - len(str(obj.start_code))
    #             chaine = ""
    #             for x in xrange(len_code):
    #                 chaine = chaine + "0"
    #             obj.encoded_start_code = int(str(obj.start_code) + chaine)
    #
    # @api.multi
    # @api.depends('end_code')
    # def _get_encoded_ec(self):
    #     for obj in self:
    #         if len(str(obj.end_code)) < 10:
    #             len_code = 10 - len(str(obj.end_code))
    #             chaine = ""
    #             for x in xrange(len_code):
    #                 chaine = chaine + "9"
    #             obj.encoded_end_code = int(str(obj.end_code) + chaine)


