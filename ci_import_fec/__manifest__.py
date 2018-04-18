# -*- coding: utf-8 -*-
# © 2017-2018 CADR'IN SITU (http://www.cadrinsitu.com/)
# @author: Tarik ARAB <tarik.arab@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'CI Account Import FEC',
    'version': '11.0.1.0.0',
    'description': """
        Ce module permetra d'importer les données comptable à partir d'un fichier FEC vers Odoo 
    """,
    'sequence': 1,
    'author': "Cadrinsitu - TA",
    'website': "http://www.cadrinsitu.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account', 'l10n_fr'],
    'data': [
        'wizard/account_import_fec_view.xml',
    ],
    'installable': True,
}