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
    frais_transport = fields.Float('TTC :', digits=dp.get_precision('Product Price'))
    frais_transport_ht = fields.Float('Frais transport HT', digits=dp.get_precision('Product Price'))
    prix_achat_ttc_hide = fields.Float('Cout revient  TTC', digits=dp.get_precision('Product Price'),
                                       store=True)
    prix_achat_ttc_hide_remise = fields.Float(digits=dp.get_precision('Product Price'),store=True)

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
    montant_marge = fields.Float(related='montant_marge_hide', string="Marge Brute",
                                 help="Marge brute = PV HT - PA HT")
    montant_marge_net =fields.Float(related='montant_marge_hide', string="Marge Nette",
                                 help="Marge Nette=PV ht - coût de revient ht")

    coef_multi_hide = fields.Float(string='Coef. multiplicateur', digits=dp.get_precision('Product Price'))
    coef_multi = fields.Float(related='coef_multi_hide', string="Coefficient multiplicateur",
                              help="PV TTC / COUT REVIENT HT")
    taux_marque_hide = fields.Float('Taux de marque', digits=dp.get_precision('Product Price'))
    taux_marque = fields.Float(related="taux_marque_hide", string="Taux de marque",
                               help="Taux de marque = (( PV HT - PA HT)) / PV HT ) * 100")
    type_tva2 = fields.Selection((('n', 'TVA Classique'), ('c', 'TVA sur marge')), 'Type de TVA', default='n')
    interaction_devise_ht = fields.Float('Interaction Devise HT ')
    interaction_devise_ttc = fields.Float('TTC :')
    remise_comerciale_ht = fields.Float('Remise Comerciale (%) ')
    remise_comerciale_ttc = fields.Float('TTC :')
    cout_packaging_ht = fields.Float('Cout de Packaging (%)', digits=dp.get_precision('Product Price'))
    cout_packaging_ttc = fields.Float('TTC :', digits=dp.get_precision('Manutention Price'))
    cout_main_oeuvre_ht = fields.Float( string="Cout Main D'oeuvre :")
    cout_main_oeuvre_ttc = fields.Float(string="TTC :")
    autre_cout_ht = fields.Float('Autre Cout HT :')
    autre_cout_ttc = fields.Float('TTC :')

    _defaults = {
        'taux_tva': 20.0,
        'taux_marge': 0.0,
        'montant_marge': 0.0,
        'montant_marge_net': 0.0,
        'taux_marque': 0.0,

    }
    @api.onchange('autre_cout_ht', 'taux_tva')
    def autre_cout_ht_change(self):
        if not self.autre_cout_ht:
            return False
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.autre_cout_ttc = self.autre_cout_ht * self.coef_tva

    @api.onchange('cout_main_oeuvre_ht', 'taux_tva')
    def cout_main_oeuvre_ht_change(self):
        if not self.cout_main_oeuvre_ht:
            return False
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.cout_main_oeuvre_ttc = self.cout_main_oeuvre_ht * self.coef_tva

    @api.onchange('cout_packaging_ht', 'taux_tva')
    def cout_packaging_ht_change(self):
        if not self.cout_packaging_ht:
            return False
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.cout_packaging_ttc = self.cout_packaging_ht * self.coef_tva
    @api.onchange('frais_transport_ht', 'taux_tva')
    def frais_transport_ht_change(self):
        if not self.frais_transport_ht:
            return False
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.frais_transport = self.frais_transport_ht * self.coef_tva
    @api.onchange('remise_comerciale_ht', 'taux_tva')
    def remise_comerciale_ht_change(self):
        if not self.remise_comerciale_ht:
            return False
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.remise_comerciale_ttc = self.remise_comerciale_ht * self.coef_tva

    @api.onchange('interaction_devise_ht', 'taux_tva')
    def interaction_devise_ht_change(self):
        if not self.interaction_devise_ht:
            return False
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.interaction_devise_ttc = self.interaction_devise_ht * self.coef_tva

    @api.onchange('prix_achat_ht', 'frais_transport', 'prix_vente_ht', 'taux_tva','remise_comerciale_ttc')
    def prix_achat_ht_change(self):
        if not self.prix_achat_ht:
            return False
        coef_tva = 1 + (self.taux_tva / 100)
        prix_achat_trans = self.prix_achat_ht + self.frais_transport

        self.prix_achat_ttc_hide = prix_achat_trans * coef_tva
        self.prix_achat_ttc_hide_remise = self.prix_achat_ttc_hide - self.remise_comerciale_ttc
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

    @api.onchange('prix_achat_ht', 'frais_transport', 'prix_vente_ht', 'taux_tva', 'montant_marge','interaction_devise_ht','interaction_devise_ttc','remise_comerciale_ht','remise_comerciale_ttc','cout_packaging_ht','cout_packaging_ttc','cout_main_oeuvre_ht','cout_main_oeuvre_ttc','autre_cout_ht','autre_cout_ttc')
    def tva_change(self):
        result = {}
        self.coef_tva = 1 + (self.taux_tva / 100)
        self.prix_achat_trans = self.prix_achat_ht + self.frais_transport
        self.prix_vente_ttc = self.prix_vente_ht * self.coef_tva
        self.interaction_devise_ttc = self.interaction_devise_ht * self.coef_tva
        self.remise_comerciale_ttc = self.remise_comerciale_ht * self.coef_tva
        self.cout_packaging_ttc = self.cout_packaging_ht * self.coef_tva
        self.cout_main_oeuvre_ttc = self.cout_main_oeuvre_ht * self.coef_tva
        self.autre_cout_ttc = self.autre_cout_ht * self.coef_tva



        self.prix_achat_ttc_hide = self.prix_achat_trans * self.coef_tva

        self.prix_achat_ttc = self.prix_achat_ttc_hide

        self.prix_vente_ttc = self.prix_vente_ttc

        if self.montant_marge > 0:
            self.coef_multi_hide = self.prix_vente_ttc / self.prix_achat_trans
            self.coef_multi = self.coef_multi_hide
        else:
            self.coef_multi_hide = 0
            self.coef_multi = self.coef_multi_hide



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

