# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO
import logging
from odoo.tools import pycompat


class InventoryImportLine(models.TransientModel):
    _name = "stock.inventory.import.line"

    name = fields.Char(string = "name")
    default_code = fields.Char('Internal Reference', index=True)
    qty = fields.Float(string="Quantity")
    product_id = fields.Many2one("product.product")
    lot_id = fields.Many2one("stock.production.lot")
    lot_name = fields.Char(string="Lot name")
    state = fields.Selection(selection=[('valid', 'valide'),
                                        ('not_valid', 'Non valide'),
                                        ('field_not_valid', 'Certains champs sont pas valides'),
                                        ('product_not_exist', 'Produit non existant'),
                                        ('product_exist', "à ajouter dans l'inventaire"),
                                        ('product_duplicate', 'Doublon'),
                                        ('lot_to_create', 'Lot à créer'),
                                        ('lot_exist', "à ajouter dans l'inventaire"),
                                       ],
                            default='valid'
                             )


class InventoryImport(models.TransientModel):
    _inherit = "bci.importer"
    _name = "stock.inventory.import"

    stock_inventory_ids = fields.Many2many('stock.inventory.import.line')
    inv_name = fields.Char('Inventory Name')
    location_id = fields.Many2one('stock.location', "Location")


    @api.multi
    def _get_stock_inventory_from_csv(self):

        stock_inventory_items = []
        list = enumerate(self.reader_info)
        logging.error('reader_info '+str(self.reader_info))
        for i, csv_line in list:
            logging.info("line %s => %s line", i, csv_line)
            if i > 0:

                product_id = self.env['product.product'].search([('default_code', '=', csv_line[0])])

                inv_item = {}
                inv_item['default_code'] = csv_line[0]
                inv_item['qty'] = csv_line[1]
                inv_item['lot_name'] = csv_line[3] if csv_line[3] else "-"
                if product_id:
                    inv_item['product_id'] = product_id[0].id
                    inv_item['state'] = 'product_exist'
                    lot_id = self._check_if_lot_exists(product_id, csv_line[3])
                    if lot_id :
                        inv_item['lot_id'] = lot_id.id
                    elif inv_item['lot_name'] != "-":
                        inv_item['state'] = 'lot_to_create'
                else:
                    inv_item['state'] = 'product_not_exist'
                if not self._is_valid_line(inv_item):
                    inv_item['state'] = 'field_not_valid'
                stock_inventory_items.append((0,0,inv_item))

        return stock_inventory_items

    @api.multi
    def get_action(self,ctx=None):
        view_id = self.env.ref("inventory_import.stock_inventory_import_form")
        action = {
            'name': ('Inventory Import'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'stock.inventory.import',
            'type': 'ir.actions.act_window',
            'target':'new'
        }
        if ctx :
            action['context']=ctx
        return action

    @api.multi
    def validate(self):
        self.get_data()

        ctx = {'default_data':self.data,
                'default_state': self.state,
                'default_inv_name': self.inv_name,
                'default_location_id': self.location_id.id,
                'default_stock_inventory_ids': self._get_stock_inventory_from_csv()
               }

        return self.get_action(ctx)

    @api.multi
    def do_import(self):

        unvalid_items = []

        line_ids = []
        for line in self.stock_inventory_ids:
            line_item = {}
            line_item['location_id'] = self.location_id.id
            line_item['product_qty'] = line.qty


            if line.state == 'product_exist':
                line_item['product_id'] = line.product_id.id
                if line.lot_name != "-":
                    line_item['prod_lot_id'] = line.lot_id.id
                line_ids.append((0, 0, line_item))

            elif line.state == "lot_to_create":
                line_item['product_id'] = line.product_id.id
                lot_item = {'product_id': line.product_id.id,
                            'name': line.lot_name,
                            }
                lot_id = self.env['stock.production.lot'].create(lot_item)
                line_item['prod_lot_id'] = lot_id.id
                line_ids.append((0, 0, line_item))
            else:
                line_item['state'] = line.state
                unvalid_items.append((0, 0, line_item))

        inv_item = {
            'state': 'draft',
            'name': self.inv_name,
            'location_id': self.location_id.id,
            'line_ids': line_ids,
            'filter': 'partial'
         }

        inv_id = self.env['stock.inventory'].create(inv_item)

        self.state = 'imported'

        return {
            'name': ('Assignment Sub'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.inventory',
            'view_id': False,
            'res_id': inv_id.id,
            'type': 'ir.actions.act_window',
        }

    def _is_valid_line(self, line):
        for  key, value in line.items():
            logging.warning("item test %s ===> %s", key, value)
            if not str(value).strip():
                return False
        return True

    def _check_if_lot_exists(self, product_id, serial_number):
        stock_prd_lot_id = self.env['stock.production.lot'].search(
            [('product_id', '=', product_id.id), ('name', '=', serial_number)])
        if len(stock_prd_lot_id) > 0:
            return stock_prd_lot_id
        else:
            return False

