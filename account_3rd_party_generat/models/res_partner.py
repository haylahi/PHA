# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
from odoo.tools.translate import _
from ..modificators import Modificator

import logging

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _partner_default_value(self, field='customer'):
        """
        Search the default context
        """
        user = self.env.user
        args = [
            ('partner_type', '=', field),
            ('default_value', '=', True),
            ('company_id', '=', user.company_id.id),
        ]
        acc_type_obj = self.env['account.generator.type']
        type_id = acc_type_obj.search(args,limit=1)
        if not type_id:
            return False
        return type_id

    @api.depends('customer','supplier','property_account_receivable_id','property_account_payable_id')
    def _get_reference(self):
        for rec in self:
            ref = ''
            customer_ref = rec.property_account_receivable_id.code if rec.property_account_receivable_id else False
            supplier_ref = rec.property_account_payable_id.code if rec.property_account_payable_id else False

            if customer_ref and rec.customer:
                if rec.customer_type:
                    ref = rec.get_refnumber(rec.customer_type,customer_ref)
            if supplier_ref and rec.supplier:
                if rec.supplier_type:
                    supplier_ref = rec.get_refnumber(rec.supplier_type,supplier_ref)
                    ref += (' / ' + supplier_ref) if rec.customer else supplier_ref

            rec.ref = ref

    def get_refnumber(self, generator, ref_number):
        prefix = generator.ir_sequence_id.prefix or ''
        partner_prefix = generator.code_pre or ''
        reference = partner_prefix + ref_number[len(prefix):]
        return reference

    customer_type = fields.Many2one(string='Customer type', company_dependent=True, comodel_name='account.generator.type', help='Customer account type')
    supplier_type = fields.Many2one(string='Supplier type', company_dependent=True, comodel_name='account.generator.type', help='Supplier account type')
    force_create_customer_account = fields.Boolean('Force create account', help='If set, OpenERP will generate a new acount for this customer', default=False)
    force_create_supplier_account = fields.Boolean('Force create account', help='If set, OpenERP will generate a new acount for this supplier', default=False)
    ref = fields.Char(string='Internal Reference', index=True, compute='_get_reference', store=True)


    @api.onchange('customer')
    def activate_generation_customer(self):
        self.customer_type = self._partner_default_value('customer')
        if self.customer:
            if self.property_account_receivable_id.id == self.customer_type.account_template_id.id:
                self.force_create_customer_account = True
        else:
            self.force_create_customer_account = False

    @api.onchange('supplier')
    def activate_generation_supplier(self):
        self.supplier_type = self._partner_default_value('supplier')
        if self.supplier:
            if self.property_account_payable_id.id == self.supplier_type.account_template_id.id:
                self.force_create_supplier_account = True
        else:
            self.force_create_supplier_account = False



    @api.multi
    def _get_compute_account_number(self, data, sequence):
        """Compute account code based on partner and sequence

        :param partner: current partner
        :type  partner: osv.osv.browse
        :param sequence: the sequence witch will be use as a pattern/template
        :type  sequence: osv.osv.browse

        :return: the account code/number
        :rtype: str
        """
        seq_patern = sequence.prefix

        if seq_patern.find('{') >= 0:
            prefix = seq_patern[:seq_patern.index('{')]
            suffix = seq_patern[seq_patern.index('}') + 1:]
            body = seq_patern[len(prefix) + 1:][:len(seq_patern) - len(prefix) - len(suffix) - 2]

            ar_args = body.split('|')

            partner = self.env['res.partner'].browse(data.get('id'))

            # partner field is always first
            partner_value = getattr(partner, ar_args[0])

            if partner_value:
                # Modificators
                mdf = Modificator(partner_value)
                for i in range(1, len(ar_args)):
                    mdf_funct = getattr(mdf, ar_args[i])
                    partner_value = mdf_funct()
                    mdf.setval(partner_value)
            account_number = "%s%s%s" % (prefix or '', partner_value or '', suffix or '')
            # is there internal sequence ?
            pos_iseq = account_number.find('#')
            if pos_iseq >= 0:
                rootpart = account_number[:pos_iseq]
                nzf = sequence.padding - len(rootpart)
                # verify if root of this number is existing
                next_inc = ("%d" % sequence.number_next).zfill(nzf)
                account_number = account_number.replace('#', next_inc)

                # Increments sequence number
                self.pool.get('ir.sequence').write([sequence.id], {'number_next': sequence.number_next + sequence.number_increment})
        else:
            account_number = sequence.next_by_id()

        return account_number

    @api.multi
    def _create_account_from_template(self, acc_value=None, acc_tmpl=None):
        """
        Compose a new account the template define on the company

        :param acc_tmpt: The account template configuration
        :type  acc_tmpl: osv.osv.browse
        :param acc_parent: The parent account to link the new account
        :type  acc_parent: integer
        :return: New account configuration
        :rtype: dict
        """
        new_account = {
            'name': acc_value.get('acc_name', 'Unknown'),
            'code': acc_value.get('acc_number', 'CODE'),
            'user_type_id': acc_tmpl.user_type_id.id,
            'reconcile': True,
            'currency_id': acc_tmpl.currency_id and acc_tmpl.currency_id.id or False,
            'active': True,
            'tax_ids': [(6, 0, [x.id for x in acc_tmpl.tax_ids])],
            'group_id':acc_tmpl.group_id and acc_tmpl.group_id.id or False,
        }
        return new_account

    @api.multi
    def _create_new_account(self, gen, data):
        """
        Create the a new account base on a company configuration

        :param type: Type of the partner (customer or supplier)
        :type  type: str
        :param data: dict of create value
        :type  data: dict
        :return: the id of the new account
        :rtype: integer
        """
        if gen:
            if gen.ir_sequence_id:
                gen_dict = {
                    'acc_name': data.get('name'),
                    'acc_number': self._get_compute_account_number(data, gen.ir_sequence_id),
                }
                new_acc = self._create_account_from_template(
                    acc_value=gen_dict,
                    acc_tmpl=gen.account_template_id
                )
                return self.env['account.account'].create(new_acc)
            else:
                return gen.account_reference_id and gen.account_reference_id.id or False


    @api.model
    def create(self, vals):
        """
        When create a customer and supplier, we create the account code
        and affect it to this partner
        """
        vals = self.generate_account(vals)

        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            self.check_lock_name(vals)
        if vals.get('force_create_customer_account') or vals.get('force_create_supplier_account'):
            vals = self.generate_account(vals)

        return super(Partner, self).write(vals)

    def check_lock_name(self, vals):
        # Check if name is allowed to be modified
        acc_move_line_obj = self.env['account.move.line']
        if vals.get('customer', self.customer):
            if self.customer_type.lock_partner_name \
                    and acc_move_line_obj.search([('account_id', '=', self.property_account_receivable_id.id)]):
                raise osv.except_osv(_('Error'),
                                     _('You cannot change partner\'s name when his account has moves'))

        if vals.get('supplier',self.supplier):
            if self.supplier_type.lock_partner_name \
                    and acc_move_line_obj.search([('account_id', '=', self.property_account_payable_id.id)]):
                raise osv.except_osv(_('Error'),
                                     _('You cannot change partner\'s name when his account has moves'))

    def generate_account(self,vals):
        data = {
            'name': vals.get('name',self.name),
            'customer_type': self._partner_default_value('customer'),
            'supplier_type': self._partner_default_value('supplier'),
        }

        if vals.get('force_create_customer_account'):
             vals['force_create_customer_account'] = False
             vals['property_account_receivable_id'] = self._create_new_account(data['customer_type'], data)
        if vals.get('force_create_supplier_account'):
             vals['force_create_supplier_account'] = False
             vals['property_account_payable_id'] = self._create_new_account(data['supplier_type'], data)

        return vals