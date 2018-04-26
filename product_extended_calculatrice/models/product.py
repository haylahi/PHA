# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Auguria (<http://www.auguria.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.exceptions import Warning
import logging
from odoo import models, fields, api
from odoo import SUPERUSER_ID
from lxml import etree

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prix_achat_ht = fields.Float('Prix achat HT', digits=dp.get_precision('Product Price'))
    frais_transport = fields.Float('Frais transport HT', digits=dp.get_precision('Product Price'))
    prix_achat_ttc_hide = fields.Float('Cout revient  TTC', digits=dp.get_precision('Product Price'),
                                       store=True)
    prix_achat_ttc = fields.Float(related='prix_achat_ttc_hide', string="Cout revient  TTC",
                                  help="(PA HT + frais transport) + TVA")
    taux_tva = fields.Float('Taux tva', digits=dp.get_precision('Product Price'))
    cout_manutention = fields.Float('Manutention Price', digits=dp.get_precision('Manutention Price'))
    prix_vente_ht = fields.Float('Prix vente HT', digits=dp.get_precision('Product Price'))
    prix_vente_ttc = fields.Float('Prix vente TTC', digits=dp.get_precision('Product Price'))
    taux_marge = fields.Float('Taux de marge', digits=dp.get_precision('Product Price'),
                              help="Taux de marge = (( PV HT - PA HT)) / PA HT ) * 100")

    montant_marge_hide = fields.Float('Marge brute', digits=dp.get_precision('Product Price'), )
    montant_audit = fields.Float('Cout Audit', digits=dp.get_precision('Audit Price'), )
    montant_marge = fields.Float(related='montant_marge_hide', string="Marge brute sur PV",
                                 help="Marge brute = PV HT - PA HT")
    coef_multi_hide = fields.Float(string='Coef. multiplicateur', digits=dp.get_precision('Product Price'))
    coef_multi = fields.Float(related='coef_multi_hide', string="Coefficient multiplicateur",
                              help="PV TTC / COUT REVIENT HT")
    taux_marque_hide = fields.Float('Taux de marque', digits=dp.get_precision('Product Price'))
    taux_marque = fields.Float(related="taux_marque_hide", string="Taux de marque",
                               help="Taux de marque = (( PV HT - PA HT)) / PV HT ) * 100")
    type_tva2 = fields.Selection((('n', 'TVA Classique'), ('c', 'TVA sur marge')), 'Type de TVA', default='n')

    _defaults = {
        'taux_tva': 20.0,
        'taux_marge': 0.0,
        'montant_marge': 0.0,
        'taux_marque': 0.0,

    }

    @api.onchange('prix_achat_ht', 'frais_transport', 'prix_vente_ht', 'taux_tva')
    def prix_achat_ht_change(self):
        if not self.prix_achat_ht:
            return False
        coef_tva = 1 + (self.taux_tva / 100)
        prix_achat_trans = self.prix_achat_ht + self.frais_transport

        self.prix_achat_ttc_hide = prix_achat_trans * coef_tva
        self.prix_achat_ttc = self.prix_achat_ttc_hide

        self.montant_marge = self.prix_vente_ht - prix_achat_trans
        self.montant_marge_hide = self.montant_marge

        if self.montant_marge > 0:
            self.taux_marge = (self.montant_marge / prix_achat_trans) * 100
            self.taux_marque_hide = (self.montant_marge / self.prix_vente_ht) * 100
            self.taux_marque = self.taux_marque_hide

            self.prix_vente_ttc = self.prix_vente_ht * coef_tva
            self.coef_multi_hide = self.prix_vente_ttc / prix_achat_trans
            self.coef_multi = self.coef_multi_hide
        else:
            self.taux_marge = 0
            self.coef_multi_hide = 0
            self.coef_multi = self.coef_multi_hide
            self.taux_marque_hide = 0
            self.taux_marque = self.taux_marque_hide

    @api.onchange('prix_achat_ht', 'frais_transport', 'prix_vente_ht', 'taux_tva', 'montant_marge')
    def tva_change(self):
        result = {}
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.prix_achat_trans = self.prix_achat_ht + self.frais_transport
        self.prix_vente_ttc = self.prix_vente_ht * self.coef_tva

        self.prix_achat_ttc_hide = self.prix_achat_trans * self.coef_tva
        self.prix_achat_ttc = self.prix_achat_ttc_hide

        self.prix_vente_ttc = self.prix_vente_ttc

        if self.montant_marge > 0:
            self.coef_multi_hide = self.prix_vente_ttc / self.prix_achat_trans
            self.coef_multi = self.coef_multi_hide
        else:
            self.coef_multi_hide = 0
            self.coef_multi = self.coef_multi_hide

        # return {'value': result}

    @api.onchange('prix_achat_ht', 'frais_transport', 'prix_vente_ht', 'taux_tva')
    def prix_vente_ht_change(self):
        result = {}
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.prix_achat_trans = self.prix_achat_ht + self.frais_transport

        self.prix_vente_ttc = self.prix_vente_ht * self.coef_tva
        self.prix_vente_ttc = self.prix_vente_ttc
        self.montant_marge = self.prix_vente_ht - self.prix_achat_trans

        self.montant_marge_hide = self.montant_marge
        self.montant_marge = self.montant_marge_hide

        if self.montant_marge > 0:
            self.taux_marge = self.montant_marge / self.prix_achat_trans * 100
            self.taux_marque_hide = self.montant_marge / self.prix_vente_ht * 100
            self.taux_marque = self.taux_marque_hide
            self.coef_multi_hide = self.prix_vente_ttc / self.prix_achat_trans
            self.coef_multi = self.coef_multi_hide
        else:
            self.taux_marge = 0
            self.coef_multi_hide = 0
            self.coef_multi = self.coef_multi_hide
            self.taux_marque_hide = 0
            self.taux_marque = self.taux_marque_hide

        # return {'value': result}

    @api.onchange('prix_vente_ttc', 'prix_achat_ht', 'frais_transport', 'taux_tva')
    def prix_vente_ttc_change(self):
        result = {}
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.prix_achat_trans = self.prix_achat_ht + self.frais_transport

        self.prix_vente_ht = self.prix_vente_ttc / self.coef_tva
        self.prix_vente_ht = self.prix_vente_ht
        self.montant_marge = self.prix_vente_ht - self.prix_achat_trans
        self.montant_marge_hide = self.montant_marge
        self.montant_marge = self.montant_marge_hide

        if self.montant_marge > 0:
            self.taux_marge = (self.montant_marge / self.prix_achat_trans) * 100
            self.taux_marque_hide = (self.montant_marge / self.prix_vente_ht) * 100
            self.taux_marque = self.taux_marque_hide
            self.coef_multi_hide = self.prix_vente_ttc / self.prix_achat_trans
            self.coef_multi = self.coef_multi_hide
        else:
            self.taux_marge = 0
            self.coef_multi_hide = 0
            self.coef_multi = self.coef_multi_hide
            self.taux_marque_hide = 0
            self.taux_marque = self.taux_marque_hide

        # return {'value': result}

    @api.onchange('prix_achat_ht', 'frais_transport', 'frais_transport', 'taux_marge', 'taux_tva')
    def taux_marge_change(self):
        result = {}
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.coef_marge = 1 + (self.taux_marge / 100)
        self.prix_achat_trans = self.prix_achat_ht + self.frais_transport

        self.prix_vente_ht = self.prix_achat_trans * self.coef_marge
        self.prix_vente_ht = self.prix_vente_ht
        self.prix_vente_ttc = self.prix_vente_ht * self.coef_tva
        self.prix_vente_ttc = self.prix_vente_ttc

        self.montant_marge = self.prix_vente_ht - self.prix_achat_trans
        self.montant_marge_hide = self.montant_marge
        self.montant_marge = self.montant_marge_hide

        if self.montant_marge > 0:
            self.coef_multi_hide = self.prix_vente_ttc / self.prix_achat_trans
            self.coef_multi = self.coef_multi_hide
            self.taux_marque_hide = (self.montant_marge / self.prix_vente_ht) * 100
            self.taux_marque = self.taux_marque_hide
        else:
            self.coef_multi_hide = 0
            self.coef_multi = self.coef_multi_hide
            self.taux_marque_hide = 0
            self.taux_marque = self.taux_marque_hide

        # return {'value': result}

# class product_supplierinfo(osv.osv):
#   _name = "product.supplierinfo"
#   _inherit = "product.supplierinfo"
#      
#   def name_get(self, cr, uid, ids, context=None):
#       if not ids:
#           return []
#       if isinstance(ids, (int, long)):
#                   ids = [ids]
#       reads = self.read(cr, uid, ids, ['name'], context=context)
#       res = []
#       for record in reads:
#           name = record['name']
#           res.append((record['id'], name))
#       return res


# class product_product(osv.osv):
#    _inherit = "product.product"

# le champs reference interne devient obligatoire
#    _columns = {
#       'default_code' : fields.char('Internal Reference', select=True, required=True),
#  }
