# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import stock with Serial number/Lot number',
    'version': '11.0.1.0',
    'sequence': 4,
    'summary': 'This module helps to import serial number with stock inventory using csv or excel file',
    "price": 45,
    "currency": 'EUR',
    'category' : 'Warehouse',
    'description': """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module is useful for import inventory with serial number from Excel and CSV file .
        Its also usefull for import opening stock balance with serial number from XLS or CSV file.
	-Import Stock from CSV and Excel file.
        -Import Stock inventory from CSV and Excel file.
	-Import inventory adjustment, import stock balance
	-Import opening stock balance from CSV and Excel file.
	-Inventory import from CSV, stock import from CSV, Inventory adjustment import, Opening stock import. Import warehouse stock, Import product stock.Manage Inventory, import inventory with lot number, import inventory with serial number, import inventory adjustment with serial number, import inventory adjustment with lot number. import inventory data, import stock data, import opening stock with lot number, import lot number, import serial number. 

هذه الوحدة مفيدة لجرد الاستيراد مع الرقم التسلسلي من ملف Excel و CSV.
         لها أيضا مفيدة لتوازن رصيد فتح الواردات مع الرقم التسلسلي من XLS أو ملف CSV.
-استيراد الأسهم من ملف CSV و Excel.
         -استيراد مخزون المخزون من ملف CSV و Excel.
-مستوى الجرد الاستيراد ، رصيد المخزون الاستيراد
-استيراد رصيد المخزون الافتتاحي من ملف CSV و Excel.
الاستيراد -Inventory من CSV ، استيراد الأوراق المالية من CSV ، استيراد تعديل المخزون ، فتح استيراد المخزون. استيراد مخزون المستودع ، استيراد مخزون المنتجات.إدارة المخزون ، جرد الاستيراد مع رقم اللوت ، جرد الاستيراد مع الرقم التسلسلي ، تعديل المخزون الاستيراد مع الرقم التسلسلي ، تعديل المخزون الاستيراد مع عدد الكثير. استيراد بيانات المخزون ، وبيانات المخزون الاستيراد ، فتح مخزون الاستيراد مع رقم الكثير ، ورقم استيراد الكثير ، واستيراد الرقم التسلسلي.

Este módulo es útil para el inventario de importación con el número de serie del archivo Excel y CSV.
         También es útil para la importación de saldos iniciales con número de serie de archivo XLS o CSV.
-Importar Stock desde CSV y archivo de Excel.
         Inventario de acciones de archivo CSV y Excel.
- Ajuste de inventario de importación, balance de stock de importación
-Importar la apertura de stock de CSV y archivo de Excel.
- Inventario importado de CSV, importación de stock desde CSV, importación de ajuste de inventario, apertura de stock de importación. Importar stock de almacén, Importar inventario de producto. Administrar inventario, importar inventario con número de lote, importar inventario con número de serie, importar ajuste de inventario con número de serie, importar ajuste de inventario con número de lote. importar datos de inventario, importar datos de stock, importar stock de apertura con número de lote, número de lote de importación, número de serie de importación.

Ce module est utile pour importer un inventaire avec un numéro de série à partir d'un fichier Excel et CSV.
         Il est également utile pour importer le solde d'ouverture avec le numéro de série du fichier XLS ou CSV.
-Import Stock à partir de fichiers CSV et Excel.
         -Import Stock d'inventaire à partir de fichiers CSV et Excel.
-Ajustement de l'inventaire des importations, importation du solde du stock
- Importer le solde du stock d'ouverture du fichier CSV et Excel.
-Inventaire d'importation de CSV, importation d'actions de CSV, importation d'ajustement d'inventaire, importation d'actions d'ouverture. Stock d'entrepôt d'importation, stock d'importation de produit. Gérer l'inventaire, importer l'inventaire avec le numéro de lot, importer l'inventaire avec le numéro de série, importer l'ajustement d'inventaire avec le numéro de série, importer l'ajustement d'inventaire avec le numéro de lot. importer des données d'inventaire, importer des données de stock, importer des actions d'ouverture avec le numéro de lot, importer le numéro de lot, importer le numéro de série.

Este módulo é útil para inventário de importação com o número de série do arquivo Excel e CSV.
         Também é útil para importar o saldo do estoque de abertura com o número de série do arquivo XLS ou CSV.
-Importar estoque do arquivo CSV e Excel.
         - Inventário de inventário de estoque do arquivo CSV e Excel.
- Ajuste de estoque de importação, saldo de estoque de importação
- Importe o saldo do estoque inicial do arquivo CSV e Excel.
- Importação de inventário de CSV, importação de estoque de CSV, importação de ajuste de estoque, importação de estoque de abertura. Estoque de armazém de importação, estoque de estoque de importação. Estoque de inventário, inventário de importação com número de lote, inventário de importação com número de série, importação de inventário com número de série, importação de inventário com número de lote. importar dados de inventário, importar dados de estoque, importar estoque de abertura com número de lote, importar número de lote, importar número de série.



    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','stock'],
    'external_dependencies':["xlrd"],
    'data': ["views/stock_view.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
}
