# -*- coding: utf-8 -*-


{
    'name': 'PHA Product Best Price',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA Product Modification ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",


    'depends': ['product','product_supplierinfo_discount'],
    'data': [

        'views/product_views.xml',
        'views/rate_views.xml',
    ],

    'installable': True,
}