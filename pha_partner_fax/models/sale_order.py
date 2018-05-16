# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    category_id = fields.Many2many(string='Étiquettes',related='partner_id.category_id',readonly=True)
    contact_id = fields.Many2many('res.partner',string='Contact')

    # @api.multi
    # def action_confirm(self):
    #     self.ensure_one()
    #     res = super(SaleOrder, self).action_confirm()
    #     self.env['stock.picking'].create({'contact': self.contact.id})
    #     return res

    #
    # @api.multi
    # def _prepare_invoice(self):
    #     """
    #     Prepare the dict of values to create the new invoice for a sales order. This method may be
    #     overridden to implement custom invoice generation (making sure to call super() to establish
    #     a clean extension chain).
    #     """
    #     self.ensure_one()s
    #     journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
    #     if not journal_id:
    #         raise UserError(_('Please define an accounting sales journal for this company.'))
    #     invoice_vals = {
    #         'name': self.client_order_ref or '',
    #         'origin': self.name,
    #         'type': 'out_invoice',
    #         'account_id': self.partner_invoice_id.property_account_receivable_id.id,
    #         'partner_id': self.partner_invoice_id.id,
    #         'partner_shipping_id': self.partner_shipping_id.id,
    #         'journal_id': journal_id,
    #         'currency_id': self.pricelist_id.currency_id.id,
    #         'comment': self.note,
    #         'payment_term_id': self.payment_term_id.id,
    #         'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
    #         'company_id': self.company_id.id,
    #         'user_id': self.user_id and self.user_id.id,
    #         'team_id': self.team_id.id,
    #         'contact_id':self.contact_id.id
    #     }
    #     return invoice_vals
