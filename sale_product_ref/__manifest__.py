# -*- coding: utf-8 -*-


{
    'name': 'Sale Product Refs',
    'version': '1.0.0',
    'author': "AgilOrg",
    'website': 'http://www.agilorg.com',
    'category': 'Sale Management',
    'depends': [
        'sale','mrp_repair'
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/sale_order_view.xml",
        "views/mrp_repair_order_view.xml",
        "reports/mrp_repair_templates_repair_order.xml",
        "reports/report_stockpicking_operations.xml",
        "reports/report_deliveryslip.xml",
    ]
}
