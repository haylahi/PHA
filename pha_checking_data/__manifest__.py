# -*- coding: utf-8 -*-
# © 2017-2018 CADR'IN SITU (http://www.cadrinsitu.com/)
# @author: Tarik ARAB <tarik.arab@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'PHA Checking DATA',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA Checking DATA ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",

    'depends': ['product', 'website_sale'],

    'data': [
        'views/res_partner_views.xml',
        'views/product_views.xml',
    ],

    'installable': True,
}