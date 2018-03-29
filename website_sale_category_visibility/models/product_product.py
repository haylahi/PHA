# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import request
from odoo import api, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}

        if 'website_id' in context:
            cat = request.env.user.partner_id.allowed_product_categories
            args += [('public_categ_ids', 'in', cat.ids)]

        return super(ProductProduct, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )
