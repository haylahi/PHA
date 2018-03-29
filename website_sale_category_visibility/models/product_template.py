# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import request
from odoo import api, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}

        if 'website_id' in context:
            cat = request.env.user.partner_id.sudo().allowed_product_categories
            args += [('public_categ_ids', 'in', cat.ids)]

        return super(ProductTemplate, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )
