# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerHCategory(models.Model):

    _inherit = 'res.partner.hcategory'

    product_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        string='Allowed Product Categories',
    )

    inherited_product_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        string='Inherited Product Categories',
        compute='_compute_inherited_product_category_ids',
    )

    def _compute_inherited_product_category_ids(self):
        for rec in self:
            allowed_category_ids = []
            hparent_id = rec.parent_id

            while hparent_id:
                allowed_category_ids += hparent_id.product_category_ids.ids
                hparent_id = hparent_id.parent_id

            rec.inherited_product_category_ids = [(6, 0, allowed_category_ids)]
