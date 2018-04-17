# -*- coding: utf-8 -*-
{
    'name': 'PHA Partner Fax',
    'version': '0.1',
    'category': 'Product Management',

    'summary': 'PHA Partner Fax ',
    'sequence': 1,
    'author': "Cadrinsitu",
    'website': "http://www.cadrinsitu.com",

    'depends': ['base_vat','l10n_fr'],
# l10n_fr est requis pour rendre le champs siret (onglet 'Ventes & Achats' invisible sur la fiche partner

    'data': [
        'views/partner.xml',
        'views/sale_order.xml',
    ],

    'installable': True,
}