# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
import base64, csv
from io import BytesIO, StringIO
import datetime
import logging
from odoo.tools import pycompat

class CsvImport(models.TransientModel):
    _name = "bci.importer"

    data = fields.Binary('File',
                         states={'draft': [('required', True)]}, required=False,
                         default=lambda self: self._context.get('data'))
    name = fields.Char('Filename')
    encoding = fields.Selection(selection='_get_encondings', string='Encoding', states={'draft': [('required', True)]}, required=False)
    delimeter = fields.Selection([(',', 'Virgule ","'),
                                  (';', 'Point virgule ";"')
                                  ]
                                 ,'Delimeter',
                            default=',')

    quotechar = fields.Selection([("'", "simple quote '"),
                                  ('"', 'double quote "')
                                  ]
                                 ,'Quotechar',
                            default="'")

    lineterminator = fields.Char('Line terminator',
                                 default='\n',
                                 help='Default delimeter is "\n"')

    state = fields.Selection(selection=[('draft', 'Brouillon'),
                                        ('validated', 'Validation'),
                                        ('imported', 'Importation')],
                             default=lambda self: self._context.get('state', 'draft')
                             )

    reader_info = []

    def _get_encondings(self):
        ''' override this if you want to add more encodings'''
        ENCODING = [
                ('iso8859_10', 'Windows Excel'),
                ('latin_1', 'Europe France'),
                ('iso8859_15', 'Europe France - Euro'),
                ('iso8859_6', 'Arabe'),
                ('utf_8', 'Unicode - utf-8'),
                ('utf_16', 'Unicode - utf-16'),
            ]
        return ENCODING

    @api.multi
    def get_data(self):
        if not self.data:
            raise exceptions.Warning(_("You need to select a file!"))
        csv_data = base64.b64decode(self.data)
        csv_data = BytesIO(csv_data.decode(self.encoding).encode('utf-8'))
        csv_iterator = pycompat.csv_reader(csv_data, quotechar=self.quotechar, delimiter=self.delimeter)

        try:
            self.reader_info = []
            self.reader_info.extend(csv_iterator)
            csv_data.close()
            self.state = 'validated'
        except Exception as e:
            raise ValidationError(_("CSV file error : %s") %e)


    @api.multi
    def validate(self):
        ''' validation step '''
        return True

    @api.multi
    def do_import(self):
        ''' Import logic here '''

        return True
