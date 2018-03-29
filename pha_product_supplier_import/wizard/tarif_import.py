# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO, StringIO
import datetime
import logging
from odoo.tools import pycompat


class TarifLine(models.TransientModel):
    _name = "tarif.line"

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade', oldname='product_id')
    min_qty = fields.Float('Minimal Quantity', default=0.0, required=True)
    max_qty = fields.Float('Maximal Quantity', default=0.0, required=True)
    product_name = fields.Char('Vendor Product Name')
    product_code = fields.Char('Vendor Product Code')
    price = fields.Float('Price', default=0.0,required=True)
    discount = fields.Float(string='Discount (%)')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    state = fields.Selection(selection=[('valid', 'valid'),
                                        ('not_valid', 'not valid'),
                                        ('imported', 'imported'),
                                        ('not_imported', 'not imported'),
                                        ],default='valid')


class TarifImport(models.TransientModel):
    _name = "tarif.import"

    data = fields.Binary('Fichier',
                         required=True,
                         default=lambda self: self._context.get('data'))
    name = fields.Char('Filename')
    encoding = fields.Selection([('iso8859_10','Windows Excel'),
                                  ('latin_1','Europe France'),
                                  ('iso8859_15','Europe France - Euro'),
                                  ('iso8859_6','Arabe'),
                                  ('utf_8','Unicode - utf-8'),
                                  ('utf_16','Unicode - utf-16'),
                                  ],'Encodage Caractères ',default='utf_8')
    delimeter = fields.Selection([(',', 'Virgule ","'),
                                  (';', 'Point virgule ";"')]
                                 ,'Delimeter',
                            default=',')

    lineterminator = fields.Char('Line terminator',
                                 default='\n',
                                 help='Default delimeter is "\n"')

    state = fields.Selection(selection=[('draft', 'Brouillon'),
                                        ('validated', 'Validation'),
                                        ('imported', 'Importation')],
                             default=lambda self: self._context.get('state', 'draft')
                             )

    reader_info = []

    tarif_ids = fields.Many2many('tarif.line',
                                 default=lambda self: self._context.get('tarifs_ids'))
    supplier_id = fields.Many2one("res.partner", readonly=True, default=lambda self: self._context.get('supplier_id'))

    @api.multi
    def _get_tarif_from_csv(self):
        tarif_items = []
        list = enumerate(self.reader_info)
        for i, csv_line in list:
            if i > 0:
                product_tmpl_id = self.env['product.template'].search([('default_code', '=', csv_line[0])])
                tarif_item = {}

                tarif_item['product_name'] = csv_line[1]
                tarif_item['product_code'] = csv_line[2]
                tarif_item['min_qty'] = csv_line[3]
                tarif_item['max_qty'] = csv_line[4]

                tarif_item['price'] = float(csv_line[5].replace(",","."))
                tarif_item['discount'] = float(csv_line[6].replace(",", "."))

                tarif_item['date_start'] = datetime.datetime.strptime(csv_line[7],'%d/%m/%Y').date()
                tarif_item['date_end'] = datetime.datetime.strptime(csv_line[8],'%d/%m/%Y').date()
                if product_tmpl_id:
                    tarif_item['state'] = 'valid'
                    tarif_item['product_tmpl_id'] = product_tmpl_id[0].id

                else:
                    tarif_item['state'] = 'not_valid'

                tarif_items.append((0, 0, tarif_item))

        return tarif_items

    @api.multi
    def validate(self):
        if not self.data:
            raise exceptions.Warning(_("You need to select a file!"))

        csv_data = base64.b64decode(self.data)
        csv_data = BytesIO(csv_data.decode(self.encoding).encode('utf-8'))
        csv_iterator = pycompat.csv_reader(csv_data, quotechar="'", delimiter=self.delimeter)

        try:
            self.reader_info = []
            self.reader_info.extend(csv_iterator)
            csv_data.close()
            self.state = 'validated'
        except Exception as e:
            print("Not a valid file!", e)
        return {
            'name': ('Tarifs'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tarif.import',
            'view_id': False,
            'context': {'data': self.data,
                        'state': self.state,
                        'supplier_id': self.supplier_id.id,
                        'tarifs_ids': self._get_tarif_from_csv()},
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.multi
    def import_tarifs(self):
        unvalid_items = []
        for tarif in self.tarif_ids:

            tarif_item = {'product_tmpl_id': tarif.product_tmpl_id.id,
                          'min_qty': tarif.min_qty,
                          'max_qty': tarif.max_qty,
                          'name': self.supplier_id.id,
                          'product_name': tarif.product_name,
                          'product_code': tarif.product_code,
                          'price': tarif.price,
                          'discount': tarif.discount,
                          'date_start': tarif.date_start,
                          'date_end': tarif.date_end,
                          }
            print ('tarif_item:',tarif_item)
            if tarif.state == 'valid':
                self.env['product.supplierinfo'].create(tarif_item)
                tarif_item['state'] = 'imported'

            else:
                tarif_item['state'] = 'not_imported'
            unvalid_items.append((0, 0, tarif_item))

        self.tarif_ids = unvalid_items
        self.state = 'imported'
        return {
            'name': ('Tarifs'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tarif.import',
            'view_id': False,
            'context': {'data': self.data,
                        'tarif_ids': unvalid_items,
                        'state': self.state},
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
