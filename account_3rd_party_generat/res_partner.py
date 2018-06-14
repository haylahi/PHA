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
from .modificators import Modificator


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _partner_default_value(self, field='customer'):
        """
        Search the default context
        """
        user = self.env['res.users'].browse(self.ids[0])
        args = [
            ('partner_type', '=', field),
            ('default_value', '=', True),
            ('company_id', '=', user.company_id.id),
        ]
        acc_type_obj = self.env['account.generator.type']
        type_ids = acc_type_obj.search(args)
        if not type_ids:
            return False
        elif len(type_ids) > 1:
            raise osv.except_osv(_('Error'), _('Too many default values defined for %s type') % _(field))
        return type_ids[0]


    customer_type = fields.Many2one(string='Customer type', company_dependent=True, comodel_name='account.generator.type', default=lambda self: self._partner_default_value('customer'), help='Customer account type')
    supplier_type = fields.Many2one(string='Supplier type', company_dependent=True, comodel_name='account.generator.type', default=lambda self: self._partner_default_value('supplier'), help='Supplier account type')
    force_create_customer_account = fields.Boolean('Force create account', help='If set, OpenERP will generate a new acount for this customer', default=False)
    force_create_supplier_account = fields.Boolean('Force create account', help='If set, OpenERP will generate a new acount for this supplier', default=False)
    # account_changed = fields.Boolean('Account changed', default=False)


    #----------------------------------------------------------
    #   Private methods C&S
    #----------------------------------------------------------

    # @api.onchange('force_create_customer_account')
    # def account_customer_changed(self):
    #     if self.force_create_customer_account == True :
    #         super(Partner, self).write({'account_changed': False})
    #
    # @api.onchange('force_create_supplier_account')
    # def account_supplier_changed(self):
    #     if self.force_create_supplier_account == True:
    #         super(Partner, self).write({'account_changed': False})



    @api.onchange('customer')
    def activate_generation_customer(self):
        if self.customer == True:
            self.force_create_customer_account = True
        else:
            self.force_create_customer_account = False

    @api.onchange('supplier')
    def activate_generation_supplier(self):
        if self.supplier == True:
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
            seq_obj = self.env['ir.sequence']
            account_number = seq_obj.get_id(sequence.id)

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
            # 'parent_id': acc_parent,
            'user_type_id': acc_tmpl.user_type_id.id,
            'reconcile': True,
            'currency_id': acc_tmpl.currency_id and acc_tmpl.currency_id.id or False,
            'active': True,
            # 'type': acc_tmpl.type,
            'tax_ids': [(6, 0, [x.id for x in acc_tmpl.tax_ids])],
            # ajout du groupe
            'group_id':acc_tmpl.group_id and acc_tmpl.group_id.id or False,
        }
        return new_account

    @api.multi
    def _get_acc_type_id(self, type=None, data=None):
        """
        Retrieve account id
        Returns account id or False
        """
        if data is None:
            data = {}
        # Set args to select account type
        args = [('partner_type', '=', type),]
        if type == 'customer':
            args.append(('id', '=', data.get('customer_type', False)))
        elif type == 'supplier':
            args.append(('id', '=', data.get('supplier_type', False)))
        # Retrieve account type id
        acc_type_obj = self.env['account.generator.type']
        type_ids = acc_type_obj.search(args)
        # If only one ID is found, return it
        if type_ids and len(type_ids) == 1:
            return type_ids[0]
        # No ID found or more than one, return False (error)
        return False

    @api.multi
    def _create_new_account(self, type=None, data=None):
        """
        Create the a new account base on a company configuration

        :param type: Type of the partner (customer or supplier)
        :type  type: str
        :param data: dict of create value
        :type  data: dict
        :return: the id of the new account
        :rtype: integer
        """
        if data is None:
            data = {}
        type_id = self._get_acc_type_id(type, data)
        if type_id:
            acc_type_obj = self.env['account.generator.type']
            gen = type_id
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
        return False

    @api.model
    def create(self, vals):
        """
        When create a customer and supplier, we create the account code
        and affect it to this partner
        """
        data = {
            'id': vals.get('id', self.id),
            'name': vals.get('name', self.name),
            'customer_type': vals.get('customer_type', self.customer_type.id),
            'supplier_type': vals.get('supplier_type', self.supplier_type.id),
        }
        if vals.get('customer', self.customer):
            vals['force_create_customer_account'] = False
            vals['property_account_receivable_id'] = self._create_new_account('customer', data)
        if vals.get('supplier', self.supplier):
            vals['force_create_supplier_account'] = False
            vals['property_account_payable_id'] = self._create_new_account('supplier', data)

        res = super(Partner, self).create(vals)
        return res

    @api.multi
    def write(self, vals=None):
        # if self._context is None:
        #     context = {}
        if vals is None:
            vals = {}
        acc_move_line_obj = self.env['account.move.line']
        if 'name' in vals:
            # Check if name is allowed to be modified
            for pnr in self:
                data = {
                    'customer_type': vals.get('customer_type', pnr.customer_type.id),
                    'supplier_type': vals.get('supplier_type', pnr.supplier_type.id),
                }
                if (pnr.customer or vals.get('customer', False) == 1):
                    acc_type_id = self._get_acc_type_id('customer', data)
                    if acc_type_id:
                        locked = self.env['account.generator.type'].read([acc_type_id], ['lock_partner_name'])
                        # Check if account type locks partner's name and if partner account has at least one move
                        if (len(locked) == 1) \
                            and ('lock_partner_name' in locked[0]) \
                            and locked[0]['lock_partner_name'] \
                            and acc_move_line_obj.search([('account_id', '=', pnr.property_account_receivable_id.id)]):
                                raise osv.except_osv(_('Error'), _('You cannot change partner\'s name when his account has moves'))
                if (pnr.supplier or vals.get('supplier', False) == 1):
                    acc_type_id = self._get_acc_type_id('supplier', data)
                    if acc_type_id:
                        locked = self.env['account.generator.type'].read([acc_type_id], ['lock_partner_name'])
                        # Check if account type locks partner's name and if partner account has at leasr one move
                        if (len(locked) == 1) \
                            and ('lock_partner_name' in locked[0]) \
                            and locked[0]['lock_partner_name'] \
                            and acc_move_line_obj.search([('account_id', '=', pnr.property_account_payable_id.id)]):
                                raise osv.except_osv(_('Error'), _('You cannot change partner\'s name when his account has moves'))
        res = True
        for partner in self :
            if vals.get('force_create_customer_account', partner.force_create_customer_account) or vals.get('force_create_supplier_account', partner.force_create_supplier_account):
                data = {
                    'id': vals.get('id', partner.id),
                    'name': vals.get('name', partner.name),
                    'customer_type': vals.get('customer_type', partner.customer_type.id),
                    'supplier_type': vals.get('supplier_type', partner.supplier_type.id),
                }
                if vals.get('customer', partner.customer) and vals.get('force_create_customer_account', partner.force_create_customer_account):
                     vals['force_create_customer_account'] = False
                     vals['property_account_receivable_id'] = self._create_new_account('customer', data)
                if vals.get('supplier', partner.supplier) and vals.get('force_create_supplier_account', partner.force_create_supplier_account):
                     vals['force_create_supplier_account'] = False
                     vals['property_account_payable_id'] = self._create_new_account('supplier', data)
                if not super(Partner, self).write(vals):
                    res = False
                    return res
                
        return super(Partner, self).write(vals)


