# -*- coding: utf-8 -*-
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