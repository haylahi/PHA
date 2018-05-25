# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    category_id = fields.Many2many(string='Étiquettes',related='partner_id.category_id',readonly=True)
    contact_id = fields.Many2one('res.partner',string='Contact')

    # @api.multi
    # def _action_confirm(self):
    #     super(SaleOrder, self)._action_confirm()
    #     for order in self:
    #         order.picking_ids.write({'contact_id': self.contact_id.id or False})

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['contact_id']= self.contact_id.id or False
        return res
