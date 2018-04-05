# -*- coding: utf-8 -*-


{
    'name': 'PHA Product features',
    'version': '11.0.1.0.0',
    'category': 'Product Management',

    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",

    'category': 'Website',
    'version': '0.1',
    'depends': ['product'],
    'data': [

        'views/product_views.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,
}