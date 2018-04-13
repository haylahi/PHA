# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _, exceptions
import logging
import csv
from itertools import groupby
from io import BytesIO, StringIO
from odoo.tools import pycompat
import io
import base64

_logger = logging.getLogger(__name__)


class CIAccountImportFECPartner(models.Model):
    _name = "ci.account.import.fec.partner"

    name = fields.Char('Name')
    partner_src = fields.Char('Partner Code Source')
    partner_dst = fields.Many2one('res.partner', string=' destination')


class CIAccountImportFECCompte(models.Model):
    _name = "ci.account.import.fec.compte"

    name = fields.Char('Name')
    compte_src = fields.Char('Account Code Source')
    compte_dst = fields.Many2one('account.account', string='Dest Account Journals',
                                 help="Let it empty if you want to import all account moves")


class CIAccountImportFECLine(models.Model):
    _name = "ci.account.import.fec.line"

    name = fields.Char('Name')
    journal_code_src = fields.Char('Journal Code Source')
    journal_code_dst = fields.Many2one('account.journal', string='Dest Account Journals',
                                       help="Let it empty if you want to import all account moves")


class AccountImportFEC(models.TransientModel):
    _name = "ci.account.import.fec"

    fec_file = fields.Binary(required=True)
    account_journal_ids = fields.Many2many('account.journal', string='Account Journals',
                                           help="Let it empty if you want to import all account moves")
    import_reconciliation = fields.Boolean(default=False)
    delimiter = fields.Char(required=True, default=';')
    line_ids = fields.Many2many('ci.account.import.fec.line', 'fec_line_rel', 'child_imp_id',
                                'parent_imp_id', string="Journal lines")
    account_ids = fields.Many2many('ci.account.import.fec.compte', 'fec_compte_rel', 'child_imp_id',
                                   'parent_imp_id', string="Account lines")
    partner_ids = fields.Many2many('ci.account.import.fec.partner', 'fec_partner_rel', 'child_imp_id',
                                   'parent_imp_id', string="Partner lines")
    encoding = fields.Selection([('iso8859_10', 'Windows Excel'),
                                 ('latin_1', 'Europe France'),
                                 ('iso8859_15', 'Europe France - Euro'),
                                 ('iso8859_6', 'Arabe'),
                                 ('utf_8', 'Unicode - utf-8'),
                                 ('utf_16', 'Unicode - utf-16'),
                                 ], 'Encodage Caractères ', default='latin_1')
    reader_info = []

    @api.multi
    def get_file_csv_data(self):
        self.ensure_one()
        csv_data = base64.b64decode(self.fec_file)
        csv_data = BytesIO(csv_data.decode(self.encoding).encode('utf-8'))
        csv_iterator = pycompat.csv_reader(csv_data, quotechar="'", delimiter=self.delimiter)
        file_reader = []
        try:
            self.reader_info = []
            self.reader_info.extend(csv_iterator)
            csv_data.close()
        except Exception as e:
            raise exceptions.Warning(e)

        list_values = enumerate(self.reader_info)
        for index, row in list_values:
            if not index:
                header = row
            else:
                file_reader.append(dict(zip(header, row)))

        return file_reader

    @api.multi
    @api.onchange('fec_file')
    @api.depends('line_ids', 'account_ids')
    def onchange_fec_file(self):
        for obj in self:
            import_line_obj = obj.env['ci.account.import.fec.line']
            journal_obj = obj.env['account.journal']
            import_compte_obj = obj.env['ci.account.import.fec.compte']
            account_obj = obj.env['account.account']
            import_partner_obj = obj.env['ci.account.import.fec.partner']
            partner_obj = obj.env['res.partner']

            if obj.fec_file:
                file_reader = obj.get_file_csv_data()
                journal_codes = set(list(map(lambda row: row['JournalCode'], file_reader)))
                account_codes = set(list(map(lambda row: row['CompteNum'], file_reader)))
                partner_codes = set(list(map(lambda row: row['CompAuxNum'], file_reader)))
                line_ids = []
                for y in journal_codes:
                    line_id = import_line_obj.search([('journal_code_src', '=', y)])
                    odoo_journal_id = journal_obj.search([('code', '=', y)])
                    if line_id:
                        if odoo_journal_id and odoo_journal_id.code != line_id.journal_code_dst:
                            line_id.write({'journal_code_dst': odoo_journal_id.code})
                        line_ids.append(line_id.id)
                    else:
                        if odoo_journal_id:
                            line_ids.append(import_journal_obj.create(
                                {'name': x, 'journal_code_src': x, 'journal_code_dst': odoo_journal_id.id}).id)
                        else:
                            line_ids.append(import_line_obj.create({'name': y, 'journal_code_src': y}).id)

                account_ids = []
                for x in account_codes:
                    account_id = import_compte_obj.search([('compte_src', '=', x)])
                    odoo_account_id = account_obj.search([('code', '=', x)])
                    if account_id:
                        if odoo_account_id and odoo_account_id.code != account_id.compte_dst:
                            line_id.write({'compte_dst': odoo_account_id.code})
                        account_ids.append(account_id.id)
                    else:
                        if odoo_account_id:
                            account_ids.append(import_compte_obj.create(
                                {'name': x, 'compte_src': x, 'compte_dst': odoo_account_id.id}).id)
                        else:
                            account_ids.append(import_compte_obj.create({'name': x, 'compte_src': x}).id)

                partner_ids = []
                for z in partner_codes:
                    if z:
                        partner_id = import_partner_obj.search([('partner_src', '=', z)])
                        odoo_partner_id = partner_obj.search([('ref', '=', z)])
                        if partner_id:
                            if odoo_partner_id and odoo_partner_id.ref != partner_id.partner_dst:
                                line_id.write({'partner_dst': odoo_partner_id.ref})
                            partner_ids.append(partner_id.id)
                        else:
                            if odoo_partner_id:
                                partner_ids.append(import_partner_obj.create(
                                    {'name': z, 'partner_src': z, 'partner_dst': odoo_partner_id.id}).id)
                            else:
                                partner_ids.append(import_partner_obj.create({'name': z, 'partner_src': z}).id)
                obj.line_ids = line_ids
                obj.account_ids = account_ids
                obj.partner_ids = partner_ids

    @api.multi
    def import_fec(self):
        self.ensure_one()
        if not self.fec_file:
            raise exceptions.Warning(_("You need to select a FEC file!"))
        file_reader = self.get_file_csv_data()

        self._filter_data(file_reader)
        return self._import_data(file_reader)

    @api.multi
    def _filter_data(self, data):
        self.ensure_one()
        journal_codes = set(list(map(lambda row: row['JournalCode'], data)))
        account_codes = set(list(map(lambda row: row['CompteNum'], data)))

        logging.info("**************** Debut Verification ****************")
        self._verify_data(journal_codes, account_codes)
        self._verif_assert_balanced(data)
        logging.info("**************** Fin Verification ****************")
        if journal_codes:
            for index, row in enumerate(data):
                if row['JournalCode'] not in journal_codes:
                    del data[index]
        return True

    @api.model
    def _import_data(self, data):
        move_obj = self.env['account.move']
        moves = []
        move_ids = []
        logging.info("**************** Debut Import ****************")
        for ecritureNum, lines in groupby(data, lambda l: l['EcritureNum']):
            lines = list(lines)
            move = move_obj.create(self.get_move_account(lines))
            logging.info("---------- Import : %s Success", move)
            moves.append(move)
        logging.info("**************** Fin import ****************")
        for move in moves:
            move_ids.append(move.id)

        if self.import_reconciliation:
            logging.info("**************** Debut Lettrage ****************")
            self._reconcile(move_ids)
            logging.info("**************** Fin Lettrage ****************")

        logging.info("**************** Debut validation ****************")
        for move in moves:
            move.post()
        logging.info("**************** Fin validation ****************")

        logging.info("==================== Fin Operation d'import ====================")
        return {
            'name': _('Imported Journal Entries'),
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'view_id': 'account.action_move_journal_line',
            'target': 'self',
            'domain': [('id', 'in', move_ids)],
        }

    @api.model
    def _reconcile(self, move_ids):
        if move_ids:
            for move_id in move_ids:
                line_obj = self.env['account.move.line']
                lines_to_reconcile = line_obj.search([('is_reconcile_mapping', '=', True),
                                                      ('account_id.reconcile', '=', True),
                                                      ('move_id', '=', move_id)])

                if lines_to_reconcile:
                    for line in lines_to_reconcile:
                        if line.is_reconcile_mapping and line.fec_reconcile_mapping:
                            reconcile_id = self.env['account.full.reconcile'].search(
                                [('name', '=', line.fec_reconcile_mapping)])
                            if not reconcile_id:
                                reconcile_id = self.env['account.full.reconcile'].create(
                                    {'name': line.fec_reconcile_mapping})
                            line.write({
                                'full_reconcile_id': reconcile_id.id
                            })
                            logging.info("---------- Lettrage : %s Success", line)
        return True

    _fec_cache = {}

    @api.multi
    def get_move_lines_account(self, lines):
        list = []

        for line in lines:
            move_line_vals = {}

            if line['EcritureLet']:
                move_line_vals['fec_reconcile_mapping'] = line['EcritureLet']
                move_line_vals['is_reconcile_mapping'] = True
            if line['CompteNum']:
                account_id = self._get_account_from_line(line['CompteNum'])
                move_line_vals['account_id'] = self._get_record_id(account_id, 'account.account')
            if line['CompAuxNum']:
                partner_id = self._get_partner_from_line(line['CompAuxNum'])
                if partner_id:
                    move_line_vals['partner_id'] = self._get_record_id(partner_id, 'res.partner', 'id')
            if line['EcritureLib']:
                move_line_vals['name'] = line['EcritureLib']
            if line['Debit']:
                move_line_vals['debit'] = self._get_amount(line['Debit'])
            if line['Credit']:
                move_line_vals['credit'] = self._get_amount(line['Credit'])
            if line['Montantdevise'] or line['Idevise'] and line['Idevise'] and \
                    line['Idevise'] != self.env.user.company_id.currency_id.name:
                if line['Montantdevise']:
                    move_line_vals['amount_currency'] = self._get_amount(line['Montantdevise'], sign=True)
                elif line['Idevise']:
                    move_line_vals['currency_id'] = self._get_record_id(line['Idevise'], 'res.currency', 'name')

            list.append((0, 0, move_line_vals))
        return list

    @api.multi
    def get_move_account(self, lines):
        list = []

        # for line in lines:
        line = lines[0]
        move_vals = {}
        if line['JournalCode']:
            journal_id = self._get_journal_from_line(line['JournalCode'])
            move_vals['journal_id'] = self._get_record_id(journal_id, 'account.journal')
        if line['EcritureNum']:
            move_vals['name'] = line['EcritureNum']
        if line['EcritureDate']:
            move_vals['date'] = self._get_date(line['EcritureDate'])
        if line['PieceRef']:
            move_vals['ref'] = line['PieceRef']

        move_vals['line_ids'] = self.get_move_lines_account(lines)
        list.append((0, 0, move_vals))

        return move_vals

    @api.model
    def _get_cache(self, model, field='code'):
        company_id = self.env.user.company_id.id
        if company_id not in self._fec_cache or model not in self._fec_cache[company_id]:
            values = dict((rec[field], rec['id']) for rec in self.env[model].search_read([], [field]))
            self._fec_cache.setdefault(company_id, {})[model] = values
        return self._fec_cache[company_id][model]

    @api.model
    def _verify_data(self, journal_code, account_code):
        message = ""
        journal_codes = []
        account_codes = []

        for x in journal_code:
            line_id = self.env['ci.account.import.fec.line'].search([('journal_code_src', '=', x)])
            if not line_id or not line_id.journal_code_dst.code:
                journal_codes.append(line_id.journal_code_src)

        for y in account_code:
            account_line_id = self.env['ci.account.import.fec.compte'].search([('compte_src', '=', y)])
            if not account_line_id or not account_line_id.compte_dst.code:
                account_codes.append(account_line_id.compte_src)

        if journal_codes:
            message = message + _("Journal lines %s are not mapped with a journal code!") % journal_codes
        if account_codes:
            message = message + _("\nAccount lines %s are not mapped with an Account code!") % account_codes
        if message:
            raise exceptions.Warning(message)

        return True

    @api.multi
    def _verif_assert_balanced(self, data):
        prec = self.env['decimal.precision'].precision_get('Account')

        message = _("Cannot create unbalanced journal entry for following EcritureNum : ")
        error = False

        for ecritureNum, lines in groupby(data, lambda l: l['EcritureNum']):
            lines = list(lines)
            debit = sum(map(lambda row: self._get_amount(row['Debit']), lines))
            credit = sum(map(lambda row: self._get_amount(row['Credit']), lines))

            if abs(debit - credit) > 10 ** (-max(5, prec)):
                error = True
                message = message + "\nName = " + ecritureNum + "; Debit = " + str(debit) + "; Credit : " + str(credit)

        if error:
            raise exceptions.Warning(message)
        return True

    @api.model
    def _get_journal_from_line(self, code):
        line_id = self.env['ci.account.import.fec.line'].search([('journal_code_src', '=', code)])
        if line_id and line_id.journal_code_dst.code:
            return line_id.journal_code_dst.code
        raise exceptions.Warning(_("The line %s is not mapped with a journal code!") % code)

    @api.model
    def _get_account_from_line(self, code):
        line_id = self.env['ci.account.import.fec.compte'].search([('compte_src', '=', code)])
        if line_id and line_id.compte_dst.code:
            return line_id.compte_dst.code
        raise exceptions.Warning(_("The line %s is not mapped with an Account code!") % code)

    @api.model
    def _get_partner_from_line(self, code):
        line_id = self.env['ci.account.import.fec.partner'].search([('partner_src', '=', code)])
        if line_id and line_id.partner_dst:
            return line_id.partner_dst.id
        return False

    @api.model
    def _get_record_id(self, code, model, field='code'):
        records = self._get_cache(model, field)
        if code not in records:
            raise exceptions.Warning(_("The %s %%s doesn't exist" % self.env[model]._description) % code)
        return records[code]

    @api.model
    def _get_amount(self, value, sign=False):
        amount = eval(value.replace(',', '.') or '0.0')
        return amount if sign else abs(amount)

    @api.model
    def _get_date(self, date):
        return '%s-%s-%s' % (date[:4], date[4:6], date[6:])
