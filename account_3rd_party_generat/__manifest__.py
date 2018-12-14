# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 SISTHEO
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
#   AUTHOR : Claude Brulé for SISTHEO
#   AUTHOR : Eric VERNICHON for SISTHEO
##############################################################################

{
    'name': 'Third parties account number generation',
    'version': '1.0',
    'sequence':'1',
    'author': 'Othmane Ghandi, SYLEAM Info Services,nextma',
    'website': 'http://www.gotodoo.com',
    'category': 'Generic Modules/Accounting',
    'description': """.
    This module is automaticaly create account number in chat of account according to the partner.
    If partner is customer it generate third party account and associate this new accoun to partner.
    The same is also done for suppliers.

    Credit :
        Othmane Ghandi, EverLibre, Zeekom ,NEXTMA
""",
    'depends': [
        'base',
        'account',
        'account_accountant',
    ],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_rule_data.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'wizard/install_wizard.xml',
    ],
    'demo_xml': [],
    'active': False,
    'application':True,
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
