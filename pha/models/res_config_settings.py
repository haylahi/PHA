# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    @api.multi
    def edit_external_header(self):
        if not self.external_report_layout:
            return False
        return self._prepare_report_view_action('pha.external_layout_' + self.external_report_layout)

    @api.multi
    def change_report_template(self):
        self.ensure_one()
        template = self.env.ref('pha.pha_view_company_report_form')
        return {
            'name': _('Choose Your Document Layout'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.env.user.company_id.id,
            'res_model': 'res.company',
            'views': [(template.id, 'form')],
            'view_id': template.id,
            'target': 'new',
        }
