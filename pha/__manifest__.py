# -*- coding: utf-8 -*-


{
    'name': 'PHA',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA module specifique ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",


    'depends': ['base','sale','account'],
    'data': [
        'reports/sale_order.xml',
        # 'reports/invoice.xml',
    ],

    'installable': True,
}
