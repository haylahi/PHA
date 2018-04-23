# -*- coding: utf-8 -*-
{
    'name': "filter_date_lines_moves",

    'summary': """
        This module adds filters on months and years of a move line in accounting app  """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Cadr'in Situ",
    'website': "http://www.cadrinsitu.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting &amp; Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',  'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}