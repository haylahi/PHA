# -*- coding: utf-8 -*-


{
    'name': 'PHA Product supplier price import ',
    'version': '11.0.1.0.0',
    'category': 'Product Management',

    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",

    'category': 'Website',
    'version': '0.1',
    'depends': ['product','product_supplierinfo_discount','purchase_discount','pha_product_best_price','base_csv_importer'],
    'data': [
        'wizard/tarif_import.xml',
        'wizard/supplier_update_date.xml',
        'views/partner_views.xml',
        'views/product_views.xml',
    ],

    'installable': True,
}