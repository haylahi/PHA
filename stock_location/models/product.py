# -*- coding: utf-8 -*-
from openerp import models, fields, api
import logging


class product_template(models.Model):
    _inherit = "product.template"

    travee = fields.Char(string ="Travée")
    etagere = fields.Char(string = "Etagére")
    colonne = fields.Char(string = "colonne")
    location = fields.Char(compute= lambda self: self._compute_location()
                           )

    @api.depends('travee','colonne','etagere')
    def _compute_location(self):
        for obj in self:
            travee = obj.travee or " - "
            colonne = obj.colonne or " - "
            etagere = obj.etagere or " - "
            obj.location = str(travee)+"/"+str(colonne)+"/"+str(etagere)