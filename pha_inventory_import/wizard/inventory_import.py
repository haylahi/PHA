# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO
import logging
from odoo.tools import pycompat


class InventoryImportLine(models.TransientModel):
    _name = "pha.stock.inventory.import.line"

    travee = fields.Char(string="Travée")
    etagere = fields.Char(string="Etagére")
    colonne = fields.Char(string="colonne")
    name = fields.Char(string = "name")
    default_code = fields.Char('Internal Reference', index=True)
    destockage = fields.Boolean(Default=False)
    cost = fields.Float("Coût")
    qty = fields.Float(string="Quantity")

    state = fields.Selection(selection=[('valid', 'valid'),
                                        ('not_valid', 'Not valid'),
                                        ('field_not_valid', 'Certains champs sont pas valides'),
                                        ('product_not_exist', 'Produit ầ créer'),
                                        ('product_exist', 'Produit à mettre à jour'),
                                        ('product_duplicate', 'Doubllons'),
                                       ],
                            default='valid'
                             )


class InventoryImport(models.TransientModel):
    _inherit = "bci.importer"
    _name = "pha.stock.inventory.import"

    dest_categ = fields.Many2one("product.category",string="Destockage catégorie", required=True)
    new_prd_categ = fields.Many2one("product.category", string="Nouveau Produit", required=True)

    stock_inventory_ids = fields.Many2many('pha.stock.inventory.import.line',
                                                default=lambda self: self._context.get('stock_inventory_ids'))
    @api.multi
    def _get_stock_inventory_from_csv(self):

        stock_inventory_items = []
        list = enumerate(self.reader_info)
        logging.error('reader_info '+str(self.reader_info))
        for i, csv_line in list:
            logging.info("line %s => %s line", i, csv_line)
            if i > 0:
                product_id = self.env['product.product'].search([('default_code', '=', str(csv_line[0]).strip())])

                if not product_id:
                    standard_price = 0.0
                elif product_id and product_id[0].categ_id.id == self.dest_categ.id:
                    standard_price = 1
                else:
                    standard_price = product_id[0].standard_price

                inv_item = {}
                inv_item['default_code'] = str(csv_line[0]).strip()
                inv_item['name'] = str(csv_line[2]).strip()
                inv_item['travee'] = str(csv_line[3]).strip()
                inv_item['colonne'] = str(csv_line[4]).strip()
                inv_item['etagere'] = str(csv_line[5]).strip()
                inv_item['destockage'] = True if csv_line[1] == "OUI" else False
                inv_item['cost'] = 1.0 if csv_line[1] == "OUI" else standard_price
                inv_item['qty'] = csv_line[6]



                if not inv_item['name']:
                    inv_item['name'] = "Article à renseigner"
                if product_id:
                    inv_item['state'] = 'product_exist'
                else:
                    inv_item['state'] = 'product_not_exist'
                if not self._is_valid_line(inv_item):
                    inv_item['state'] = 'field_not_valid'



                stock_inventory_items.append((0,0,inv_item))

        for i, item in enumerate(stock_inventory_items):
            if i < len(stock_inventory_items)-1:
                if item[2]['default_code'] == str(csv_line[0]).strip():
                    inv_item['state'] = "product_duplicate"

        return stock_inventory_items


    @api.multi
    def get_action(self,ctx=None):
        view_id = self.env.ref("pha_inventory_import_.pha_stock_inventory_import_form")
        action ={
            'name': ('PHA import inventory'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'pha.stock.inventory.import',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'target': 'new'
        }
        return action

    @api.multi
    def validate(self):
        self.get_data()
        ctx = {'data':self.data,
                'state': self.state,
                'default_dest_categ': self.dest_categ.id,
                'default_new_prd_categ': self.new_prd_categ.id,
                'stock_inventory_ids': self._get_stock_inventory_from_csv()
               }
        return self.get_action(ctx)

    @api.multi
    def do_import(self):

        unvalid_items = []
        for line in self.stock_inventory_ids:

            logging.warning('line.state => ' + str(line.state))
            inv_item = {}

            inv_item['travee'] = line.travee
            inv_item['etagere'] = line.etagere
            inv_item['colonne'] = line.colonne
            inv_item['standard_price'] = line.cost
            inv_item['type'] = 'product'
            if line.destockage:
                inv_item['categ_id'] = self.dest_categ.id

            if line.state == 'product_not_exist':
                inv_item['name'] = line.name
                inv_item['default_code'] = line.default_code

                if not line.destockage:
                    inv_item['categ_id'] = self.new_prd_categ.id
                self.env['product.product'].create(inv_item)

            elif line.state == 'product_exist':
                product_id = self.env['product.product'].search([('default_code','=', line.default_code)])
                product_id[0].write(inv_item)
            else:
                inv_item['state'] = line.state
                unvalid_items.append((0,0,inv_item))

        self.state = 'imported'

        ctx = {'default_data': self.data,
                'default_stock_inventory_ids': unvalid_items,
                'default_state': self.state
               }
        return self.get_action(ctx)

    def _is_valid_line(self, line):
        for  key, value in line.items():
            logging.warning("item test %s ===> %s", key, value)
            if not str(value).strip():
                return False
        return True
