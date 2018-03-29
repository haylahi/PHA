# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):

    _inherit = 'product.pricelist'

    @api.multi
    def write(self, vals):
        self.ensure_one()
        if self.id == self.env.ref(
            'website_sale_pricelist_visibility.default_pricelist'
        ).id and 'sequence' in vals and vals['sequence'] != 0:
            raise ValidationError(
                _('You can not change sequence of default pricelist!')
            )

        return super(ProductPricelist, self).write(vals)

    @api.multi
    def unlink(self):
        default_pl_id = self.env.ref(
            'website_sale_pricelist_visibility.default_pricelist'
        ).id
        for rec in self:
            if rec.id == default_pl_id:
                raise ValidationError(
                    _('You can not delete default pricelist!')
                )
        return super(ProductPricelist, self).unlink()

    def _get_partner_pricelist(self, partner_id, company_id=None):
        """ Retrieve the applicable pricelist for a given partner in a given company.

            :param company_id: if passed, used for looking up properties,
             instead of current user's company
        """
        partner_model = self.env['res.partner']
        property_model = self.env['ir.property'].with_context(force_company=company_id or self.env.user.company_id.id)

        partner = partner_model.browse(partner_id)
        pl = property_model.get('property_product_pricelist', partner_model._name, '%s,%s' % (partner_model._name, partner.id))
        if pl:
            pl = pl[0].id

        if not pl:
            if partner.country_id.code:
                pls = self.env['product.pricelist'].search([('country_group_ids.country_ids.code', '=', partner.country_id.code)], limit=1)
                pl = pls and pls[0].id

        if not pl:
            # search pl where no country
            pls = self.env['product.pricelist'].search([('country_group_ids', '=', False)], limit=1)
            pl = pls and pls[0].id

        if not pl:
            prop = property_model.get('property_product_pricelist', 'res.partner')
            pl = prop and prop[0].id

        if not pl or pl not in partner.allowed_pricelists.ids:
            pl = self.env.ref(
                'website_sale_pricelist_visibility.default_pricelist'
            ).id

        return pl
