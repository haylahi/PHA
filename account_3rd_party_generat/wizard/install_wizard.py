# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2009 SISTHEO
#                  2010-2011 Christophe Chauvet <christophe.chauvet@syleam.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.osv import osv
from odoo import models, fields, api

import logging

import types


class wizard_install_third_part_accounts(models.TransientModel):
    """
    """
    _name = 'wizard.install.third.part.accounts'

    @api.multi
    def _default_account_id(self, account_type):
        account_type_id = self.env['account.account.type'].search([('type', '=', account_type)])
        srch_args = [('user_type_id', '=', account_type_id.id)]
        account_id = self.env['account.account'].search(srch_args)
        logging.info('##### account : %s' %account_id)
        if account_id:
            return account_id.ids
        return False

    @api.multi
    def _default_receivable_id(self):
        return [('id','in',self._default_account_id('receivable'))]

    @api.multi
    def _default_payable_id(self):
        return [('id','in',self._default_account_id('payable'))]

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, required=True)
    receivable_id = fields.Many2one('account.account', 'Account receivable', domain=lambda self: self._default_receivable_id(), required=True)
    payable_id = fields.Many2one('account.account', 'Account payable', domain=lambda self: self._default_payable_id(), required=True)


    @api.multi
    def _set_property(self, prop_name, prop_account_id, company_id):
        """
        Set/Reset default properties
        """
        property_obj = self.env['ir.property']
        prp = property_obj.search([('name', '=', prop_name), ('company_id', '=', company_id.id)])

        if prp:
            out_id = prp.write({'value_reference': 'account.account,' + str(prop_account_id.id)})

        else:  # create the property
            fields_obj = self.env['ir.model.fields']
            field_id = fields_obj.search([('name', '=', prop_name), ('model', '=', 'res.partner'), ('relation', '=', 'account.account')])
            vals = {
                'name': prop_name,
                'company_id': company_id.id,
                'fields_id': field_id.id,
                'value_reference': 'account.account,' + str(prop_account_id.id),
            }
            out_id = property_obj.create(vals)
        return out_id

    @api.multi
    def action_start_install(self):
        """
        Create the properties : specify default account (payable and receivable) for partners
        """
        self._set_property('property_account_receivable_id', self.receivable_id, self.company_id)
        self._set_property('property_account_payable_id', self.payable_id , self.company_id)

        next_action = {
            'type': 'ir.actions.act_window',
            # 'res_model': 'ir.actions.configuration.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
