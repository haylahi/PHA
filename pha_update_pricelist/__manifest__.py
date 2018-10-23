# -*- coding: utf-8 -*-
{
    'name': 'PHA update pricelist',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA module specifique ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",


    'depends': ['base','sale'],
    'data': [
       'views/product_pricelist_view.xml',
    ],

    'installable': True,
}
