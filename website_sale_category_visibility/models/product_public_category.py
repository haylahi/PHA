# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import request
from odoo import api, fields, models


class ProductPublicCategory(models.Model):

    _inherit = 'product.public.category'

    restricted_partner_category_ids = fields.Many2many(
        comodel_name='res.partner.hcategory',
        string='Restrict to Partner Categories',
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}

        if 'website_id' in context:
            cat = request.env.user.partner_id.allowed_product_categories
            args += [('id', 'in', cat.ids)]

        return super(ProductPublicCategory, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )
