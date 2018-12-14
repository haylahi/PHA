from odoo import models, fields, api
import logging


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        if self.pricelist_id.automatic_update:

            for o_l in self.order_line:
                item_exist = False
                item_to_update = None
                for item in self.pricelist_id.item_ids:
                    if item.product_tmpl_id.id == o_l.product_id.product_tmpl_id.id:
                        item_exist = True
                        if item_to_update == None and o_l.product_uom_qty > item.min_quantity:
                            item_to_update = item
                        elif o_l.product_uom_qty > item.min_quantity and item_to_update.min_quantity < item.min_quantity:
                            item_to_update = item

                        logging.warning("item_to_update %s", item_to_update)

                if not item_exist:
                    logging.warning("test of %s", item_exist)
                    res = self.env['product.pricelist.item'].create({'name': o_l.product_id.name,
                                                                     'pricelist_id':self.pricelist_id.id,
                                                                'applied_on': '1_product',
                                                                'product_tmpl_id': o_l.product_id.product_tmpl_id.id
                                                                ,'min_quantity': 0,
                                                                'fixed_price': o_l.price_unit})

                elif item_to_update and item_to_update.compute_price == 'fixed':
                    res = item_to_update.write({'fixed_price': o_l.price_unit})

        super(SaleOrder, self).action_confirm()
