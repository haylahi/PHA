# -*- coding: utf-8 -*-

{
    'name': 'Account Description',
    'version': '11.0.1.0.0',
    'description': """
        Ce module permet d'améliorer le module de vente en rajoutant des descriptions pour formule politesse ou Titre dans les Ligne devis ou facture 
    """,
    'sequence': 1,
    'author': "Cadrinsitu - TA",
    'website': "http://www.cadrinsitu.com",
    'category': 'Sale',
    'version': '0.1',
    'depends': ['sale', 'product', 'website_quote'],
    'data': [
        'views/product_views.xml',
        'views/title_product_views.xml',
        'report/sale_report_templates.xml',
        'report/website_quote_templates.xml',
        'report/invoice_report_templates.xml',
    ],
    'installable': True,
}
