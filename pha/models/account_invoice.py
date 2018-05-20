# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    max_line = fields.Integer('Nombre de lignes/page', default=10, help="Nombre maximum de lignes par page sur l'imprimé de facture.")

    @api.multi
    def order_lines_per_page(self):
        """
        Returns a list of pages by max number of lines per page.
        """
        self.ensure_one()
        report_pages =[self.invoice_line_ids[x:x+self.max_line] for x in range(0, len(self.invoice_line_ids), self.max_line)]
        pages=[]
        report=0
        for page in report_pages:
            dict= {}
            dict['subtotal'] = sum(line.price_subtotal for line in page)
            dict['lines']= page
            dict['report'] = report
            report = report + dict['subtotal']
            pages.append(dict)

        return pages

