# -*- coding: utf-8 -*-
##############################################################################
#
#    account_3rd_party_generat module for OpenERP, Module to generate account number
#                                                  for customer and supplier
#    Copyright (C) 2010-2011 SYLEAM (<http://www.syleam.fr/>)
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#
#    This file is a part of account_3rd_party_generat
#
#    account_3rd_party_generat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_3rd_party_generat is distributed in the hope that it will be useful,
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
from odoo.tools.translate import _


class AccountGeneratorType(models.Model):
    _name = 'account.generator.type'
    _description = 'Account generator customize per type'


    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], 'Type', default=False, required=True, help='Select the type of partner')
    code = fields.Char('code', size=16, required=True, help='Code use to store value in the database')
    name = fields.Char('Name', size=64, required=True, translate=True, help='Name appear on the partner form')
    default_value = fields.Boolean('Default value', default=False, help='Default value for this type')
    lock_partner_name = fields.Boolean('Lock partner name', help='Partner\'s name is locked when his account has at least one account move')
    ir_sequence_id = fields.Many2one('ir.sequence', 'Sequence', default=False, help='Sequence use to generate the code')
    account_template_id = fields.Many2one('account.account', 'Account template', default=False, help='Account use to create the new one')
    account_reference_id = fields.Many2one('account.account', 'Account reference', help='If no sequence define, this account reference is choose all the time')
    company_id = fields.Many2one('res.company', 'Company', help='Company where this configuration is apply', required=True)
    field_select = fields.Selection([('none', ''), ('name','name'), ('ref','ref')], 'Select Field', default='none', help="Select the field where the code be generate" )
    # generate_ref_partner = fields.Boolean('Generer reference partenaire')
    code_pre = fields.Char('Code Prefix', help="prefix pour la reference partenaire")
    code_suf = fields.Char('Code Suffix')
    code_seq_id = fields.Many2one('ir.sequence', 'Sequence', domain=[('code', '=', 'res.partner')])


class ResCompany(models.Model):
    _inherit = 'res.company'


    account_generator_type_ids = fields.One2many('account.generator.type', 'company_id', 'Account generator type')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
