# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    allowed_product_categories = fields.Many2many(
        comodel_name='product.public.category',
        compute='_compute_all_product_categories',
    )

    def _compute_all_product_categories(self):
        for rec in self:
            # get allowed categories for this partner category
            parent_id = rec
            while parent_id:
                partner = parent_id
                parent_id = parent_id.parent_id

            allowed_category_ids = partner.hcategory_id.product_category_ids.ids
            hparent_id = partner.hcategory_id.parent_id
            while hparent_id:
                allowed_category_ids += hparent_id.product_category_ids.ids
                hparent_id = hparent_id.parent_id
            allowed_category_ids = list(set(allowed_category_ids))
            allowed = self.env['product.public.category'].with_context({
                'in_website': False,
            }).search([
                '|',
                ('restricted_partner_category_ids', '=', False),
                ('id', 'child_of', allowed_category_ids),
            ])

            # get disallowed categories for this partner category
            denied_ids = self.env['product.public.category'].with_context({
                'in_website': False,
            }).search([
                ('restricted_partner_category_ids', '!=', False),
                ('id', 'not in', allowed.ids)
            ]).ids
            denied = self.env['product.public.category'].with_context({
                'in_website': False,
            }).search([
                ('id', 'child_of', denied_ids),
            ])

            rec.allowed_product_categories = allowed - denied

    @api.multi
    def open_partner_category(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner.hcategory',
            'view_mode': 'form',
            'res_id': self.hcategory_id.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True}}
        }
