# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO, StringIO
from datetime import datetime
import logging
from odoo.tools import pycompat
from odoo.tools.profiler import profile

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
    currency_id=fields.Many2one('res.currency',string='Devise')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    state = fields.Selection(selection=[('valid', 'valid'),
                                        ('not_valid', 'not valid'),
                                        ('imported', 'imported'),
                                        ('not_imported', 'not imported'),
                                        ],default='valid')
    import_id = fields.Many2one("tarif.import", ondelete="cascade")

class TarifImport(models.TransientModel):
    _inherit = "bci.importer"
    _name = "tarif.import"

    show_valid = fields.Boolean('Ignorer les non valides')
    encoding = fields.Selection(default='iso8859_10')

    tarif_ids = fields.One2many("tarif.line","import_id",default=lambda self: self._context.get('tarifs_ids'))
    supplier_id = fields.Many2one("res.partner", readonly=True, default=lambda self: self._context.get('supplier_id'))

    @api.multi
    def _get_currency(self,code):
        currency= self.env['res.currency'].search([('name','=',code)])
        if currency:
            return currency.id
        else :
            raise UserError(_("No currency found with code %s" %code))

    @profile
    @api.multi
    def _get_tarif_from_csv(self):
        tarif_items = []
        list = enumerate(self.reader_info)
        product_template = self.env['product.template']
        for i, csv_line in list:
            if i > 0:
                product_tmpl_id = product_template.search([('default_code', '=', csv_line[0])])
                tarif_item = {}

                # logging.info('##csv_line :%s', csv_line)
                tarif_item['product_name'] = csv_line[1]
                tarif_item['product_code'] = csv_line[2]
                tarif_item['min_qty'] = csv_line[3]
                tarif_item['max_qty'] = csv_line[4]

                tarif_item['price'] = float(csv_line[5].replace(",", "."))
                tarif_item['discount'] = float(csv_line[6].replace(",", "."))
                tarif_item['currency_id'] = self._get_currency(csv_line[7])

                tarif_item['date_start'] = datetime.strptime(csv_line[8], '%d/%m/%Y').date()
                tarif_item['date_end'] = datetime.strptime(csv_line[9], '%d/%m/%Y').date()
                if product_tmpl_id:

                    tarif_item['state'] = 'valid'
                    tarif_item['product_tmpl_id'] = product_tmpl_id[0].id
                    tarif_items.append((0, 0, tarif_item))
                    continue

                if not self.show_valid :
                    tarif_item['state'] = 'not_valid'
                    tarif_items.append((0, 0, tarif_item))

        return tarif_items

    @api.multi
    def get_action(self,ctx=None):
        view_id = self.env.ref("pha_product_supplier_import.tarif_import_form")
        action ={
            'name': ('Tarifs'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'tarif.import',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'target': 'new'
        }
        return action

    @api.multi
    def validate(self):
        self.get_data()

        ctx = {'data': self.data,
                'state': self.state,
                'supplier_id': self.supplier_id.id,
                'tarifs_ids': self._get_tarif_from_csv()
            }
        return self.get_action(ctx)

    @api.multi
    def do_import(self):
        unvalid_items = []
        supplierinfo = self.env['product.supplierinfo']
        for tarif in self.tarif_ids:

            tarif_item = {'product_tmpl_id': tarif.product_tmpl_id.id,
                          'min_qty': tarif.min_qty,
                          'max_qty': tarif.max_qty,
                          'name': self.supplier_id.id,
                          'product_name': tarif.product_name,
                          'product_code': tarif.product_code,
                          'price': tarif.price,
                          'discount': tarif.discount,
                          'currency_id': tarif.currency_id.id,
                          'date_start': tarif.date_start,
                          'date_end': tarif.date_end,
                          }
            if tarif.state == 'valid':
                supplierinfo.create(tarif_item)
                tarif_item['state'] = 'imported'

            else:
                tarif_item['state'] = 'not_imported'
            unvalid_items.append((0, 0, tarif_item))

        self.state = 'imported'

        ctx = {'data': self.data,
                'tarif_ids': unvalid_items,
                'state': self.state
            }
        return self.get_action(ctx)
