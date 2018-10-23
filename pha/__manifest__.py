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
        'wizard/supplier_update_date.xml',
        'views/report_templates.xml',
        'views/account_invoice_view.xml',
        'views/sale_order_views.xml',
        'views/res_company_view.xml',
        'views/product_template_view.xml',
        'views/stock_move_view.xml',
        'views/res_partner.xml',
        'views/mrp_repair_views.xml',
        'reports/external_templates.xml',
        'reports/report_actions.xml',
        'reports/sale_order.xml',
        'reports/invoice.xml',
        'reports/mrp_repair.xml',
        'reports/purchase_order.xml',
        'reports/deliveryslip.xml',
        'reports/stockpicking.xml',
    ],

    'installable': True,
}
