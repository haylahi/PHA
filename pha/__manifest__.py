# -*- coding: utf-8 -*-
{
    'name': 'PHA',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA module specifique ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",


    'depends': ['base','sale','account','purchase'],
    'data': [
        'views/report_templates.xml',
        'reports/external_templates.xml',
        'reports/sale_order.xml',
        'reports/invoice.xml',
        'reports/purchase_quotation_templates.xml',
        'reports/purchase_order_templates.xml',
    ],

    'installable': True,
}
