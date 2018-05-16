# -*- coding: utf-8 -*-


{
    'name': 'Stock Location',
    'version': '1.0.0',
    'author': "AgilOrg",
    'website': 'http://www.agilorg.com',
    'category': 'Sale Management',
    'depends': [
        'sale', 'sale_stock'
    ],
    'data': [
        "views/product_template.xml",
        "reports/report_stockpicking_operations.xml",
        "reports/report_deliveryslip.xml",
    ]
}
