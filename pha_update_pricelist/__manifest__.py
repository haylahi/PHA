# -*- coding: utf-8 -*-
{
    'name': 'PHA',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA module specifique ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",


    'depends': ['base','sale','sale_stock','sale_order_dates','pha_partner_fax',
                'stock','account','purchase','ci_account_desc','stock_location',
                'mrp_repair','website_sale'],
    'data': [
       'views/product_pricelist_view.xml',
        'views/mrp_repair_views.xml',
        'reports/mrp_repair.xml',    
    ],

    'installable': True,
}
