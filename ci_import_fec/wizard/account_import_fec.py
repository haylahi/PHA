# -*- coding: utf-8 -*-
# © 2017-2018 CADR'IN SITU (http://www.cadrinsitu.com/)
# @author: Tarik ARAB <tarik.arab@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo import api, fields, models, _, exceptions
import logging
import csv
from itertools import groupby
from io import BytesIO, StringIO
from odoo.tools import pycompat, float_compare, float_round
import io
import base64

_logger = logging.getLogger(__name__)

ACTION = {
    'name': _('Import FEC'),
    'type': 'ir.actions.act_window',
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'ci.account.import.fec',
    'views': [(False, 'form')],
    'target': 'new',
}


class ImportFECPartner(models.Model):
    _name = "ci.account.import.fec.partner"

    name = fields.Char('Name')
    partner_src = fields.Char('Partner Code Source')
    partner_dst = fields.Many2one('res.partner', string=' destination')
    compte_dst = fields.Many2one('account.account', string='Dest Account')

    type = fields.Selection([
        ('C', 'Client'),
        ('F', 'Fournisseur'),
    ], 'Type')

    state = fields.Selection([
        ('valid', 'Valide'),
        ('no_partner', 'Partenaire non existant'),
    ], 'Status',
        copy=False, readonly=True)


class ImportFECCompte(models.Model):
    _name = "ci.account.import.fec.compte"

    name = fields.Char('Name')
    compte_src = fields.Char('Account Code Source')
    compte_dst = fields.Many2one('account.account', string='Dest Account Journals')

    type = fields.Selection([
        ('general', 'Général'),
        ('tiers', 'Tiers'),
    ], 'Type', default='general',
        copy=False, )

    state = fields.Selection([
        ('not_valid', 'Non valide'),
        ('valid', 'Valide'),
    ], 'Status',
        copy=False, )


class ImportFECLine(models.Model):
    _name = "ci.account.import.fec.line"

    name = fields.Char('Name')
    journal_code_src = fields.Char('Journal Code Source')
    journal_name_src = fields.Char('Journal Name Source')
    journal_code_dst = fields.Many2one('account.journal', string='Dest Account Journals',
                                       help="Le journal qui sera associé à l'écriture comptable dans Odoo")

    state = fields.Selection([
        ('not_valid', 'Non valide'),
        ('valid', 'Valide'),
    ], 'Status',
        copy=False, readonly=True, required=True)


class ImportFEC(models.TransientModel):
    _name = "ci.account.import.fec"

    fec_file = fields.Binary(required=True)
    matrix_tiers_file = fields.Binary('Matrice des tiers')
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
    nbr_char = fields.Integer('Codification', default=10)
    import_auto_num = fields.Boolean(string="Regroupement automatique", default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate_journal', 'Validation Journaux'),
        ('validate_account', 'Validation Comptes'),
        ('validate_partners', 'Validation Partenaires'),
        ('configure_partners', 'Configuration Partenaires'),
        ('imported', 'Importé'),
    ], 'Status', default='draft',
        copy=False, readonly=True, required=True)

    reader_info = []

    @api.multi
    def get_file_csv_data(self, file):
        self.ensure_one()
        csv_data = base64.b64decode(file)
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
    def verification_step(self):
        self.ensure_one()
        file_reader = self.get_file_csv_data(self.fec_file)
        if self.state == 'validate_journal':
            self.verify_journal(file_reader)
            self.state = 'validate_account'
        elif self.state == 'validate_account':
            self.verify_account(file_reader)
            self.state = 'validate_partners'
        ACTION['res_id'] = self.id
        return ACTION

    @api.multi
    def preview_step(self):
        self.ensure_one()
        if self.state == 'validate_journal':
            self.state = 'draft'
        elif self.state == 'validate_account':
            self.state = 'validate_journal'
        elif self.state == 'validate_partners':
            self.state = 'validate_account'
        elif self.state == 'configure_partners':
            self.state = 'validate_partners'
        ACTION['res_id'] = self.id
        return ACTION

    @api.multi
    def load_file_step(self):
        self.ensure_one()
        if not self.fec_file:
            raise exceptions.Warning(_("You need to select a FEC file!"))
        if self.state == 'draft':
            self._load_fec_file()
            self.state = 'validate_journal'
        ACTION['res_id'] = self.id
        return ACTION

    @api.multi
    def config_partners_step(self):
        self.state = 'configure_partners'
        ACTION['res_id'] = self.id
        return ACTION

    @api.multi
    def import_fec_step(self):
        self.ensure_one()
        if self.fec_file:
            file_reader = self.get_file_csv_data(self.fec_file)
            self._filter_data(file_reader)
            logging.info('--------------------------------- %s', file_reader)
            return self._import_data(file_reader)

    @api.multi
    def _load_fec_file(self):
        for obj in self:
            logging.info("**************** DEBUT Chargement Fichier ****************")
            if obj.fec_file:
                file_reader = obj.get_file_csv_data(self.fec_file)
                obj.line_ids = obj.get_journal_lines(file_reader)
                obj.account_ids = obj.get_account_lines(file_reader)
                obj.partner_ids = obj.get_partner_lines(file_reader)
            logging.info("**************** FIN Chargement Fichier ****************")
        return True

    @api.multi
    def get_journal_lines(self, data):
        for obj in self:
            import_line_obj = obj.env['ci.account.import.fec.line']
            journal_obj = obj.env['account.journal']
            journal_codes = set(list(map(lambda row: row['JournalCode'], data)))
            line_ids = []
            for y in journal_codes:
                line_id = import_line_obj.search([('journal_code_src', '=', y)])
                odoo_journal_id = journal_obj.search([('code', '=', y)])
                if line_id:
                    if line_id.journal_code_dst and line_id.state != 'valid':
                        line_id.write({'state': 'valid'})
                    if odoo_journal_id:
                        line_id.write({'journal_code_dst': odoo_journal_id.id, 'state': 'valid'})
                    line_ids.append(line_id.id)
                else:
                    if odoo_journal_id:
                        line_ids.append(import_line_obj.create(
                            {'name': y, 'journal_code_src': y, 'journal_code_dst': odoo_journal_id.id, 'state': 'valid',
                             'type': 'general'}).id)
                    else:
                        line_ids.append(import_line_obj.create(
                            {'name': y, 'journal_code_src': y, 'state': 'not_valid', 'type': 'general'}).id)
            return line_ids

    @api.multi
    def get_account_lines(self, data):
        for obj in self:
            import_compte_obj = obj.env['ci.account.import.fec.compte']
            account_obj = obj.env['account.account']
            account_codes = set(list(map(lambda row: row['CompteNum'], data)))
            account_ids = []

            for x in account_codes:
                account_id = import_compte_obj.search([('compte_src', '=', x)])
                odoo_account_id = account_obj.search([('code', '=', x)])
                if account_id:
                    if account_id.compte_dst and account_id.state != 'valid':
                        account_id.write({'state': 'valid'})
                    if odoo_account_id:
                        account_id.write({'compte_dst': odoo_account_id.id, 'state': 'valid'})
                    account_ids.append(account_id.id)
                else:
                    if odoo_account_id:
                        account_ids.append(import_compte_obj.create(
                            {'name': x, 'compte_src': x, 'compte_dst': odoo_account_id.id, 'state': 'valid'}).id)
                    else:
                        account_ids.append(
                            import_compte_obj.create({'name': x, 'compte_src': x, 'state': 'not_valid'}).id)
            return account_ids

    @api.multi
    def get_partner_lines(self, data, matrix_data=False):
        for obj in self:
            import_partner_obj = obj.env['ci.account.import.fec.partner']
            partner_obj = obj.env['res.partner']
            partner_codes = set(list(map(lambda row: row['CompAuxNum'], data)))
            partner_ids = []
            logging.info("**************** DEBUT Configuration comptes tiers ****************")
            for z in partner_codes:
                if z:
                    if matrix_data:
                        matrix_mapped_line = self.get_value_from_data(matrix_data, 'RefSourceComptable', z)
                    partner_id = import_partner_obj.search([('partner_src', '=', z)])
                    ref = z
                    type = ""
                    if matrix_data and matrix_mapped_line:
                        ref = matrix_mapped_line['CodeRespartner']
                        code_partner = matrix_mapped_line['NouveauCompte']
                        type = matrix_mapped_line['Type']

                    odoo_partner_id = partner_obj.search([('ref', '=', ref)])
                    if odoo_partner_id and matrix_data:
                        obj.config_compte_tiers(z, code_partner, type, odoo_partner_id)

                    if partner_id:
                        # if odoo_partner_id and odoo_partner_id.ref != partner_id.partner_dst.ref:
                        if odoo_partner_id:
                            partner_id.write({'partner_dst': odoo_partner_id.id, 'type': type,
                                              'state': 'valid',
                                              'compte_dst': odoo_partner_id.property_account_receivable_id.id})
                        partner_ids.append(partner_id.id)
                    else:
                        if odoo_partner_id:
                            partner_ids.append(import_partner_obj.create({'name': z, 'partner_src': z,
                                                                          'partner_dst': odoo_partner_id.id,
                                                                          'type': type, 'state': 'valid',
                                                                          'compte_dst': odoo_partner_id.property_account_receivable_id.id}).id)
                        else:
                            partner_ids.append(
                                import_partner_obj.create({'name': z, 'partner_src': z, 'state': 'no_partner', 'type': type}).id)
            logging.info("**************** FIN Configuration comptes tiers ****************")
            return partner_ids

    @api.multi
    def config_compte_tiers(self, code_src, code, type, partner):
        account_obj = self.env['account.account']
        account_tiers_id = account_obj.search([('code', '=', code)])

        if not account_tiers_id:
            config_id = self.get_config_from_code(code)
            values = {'name': code_src, 'code': code,
                      'reconcile': config_id.reconcile}
            if config_id:
                values['user_type_id'] = config_id.user_type_id.id
            account_id = account_obj.create(values)

            if type == 'C':
                logging.info("------------------- Creation compte tiers Client: %s", account_id.name)
                partner.write({'property_account_receivable_id': account_id.id})
            elif type == 'F':
                logging.info("------------------- Creation compte tiers Fournisseur: %s", account_id.name)
                partner.write({'property_account_payable_id': account_id.id})
        else:
            if type == 'C':
                if account_tiers_id.id is not partner.property_account_receivable_id.id:
                    partner.write({'property_account_receivable_id': account_tiers_id.id})
                    logging.info("------------------- MAJ compte tiers Client: %s - %s",
                                 partner.property_account_receivable_id.name, account_tiers_id.name)
            elif type == 'F':
                if account_tiers_id.id is not partner.property_account_payable_id.id:
                    partner.write({'property_account_payable_id': account_tiers_id.id})
                    logging.info("------------------- MAJ compte tiers Fournisseur: %s",
                                 partner.property_account_payable_id.name)
        # return True

    @api.multi
    def load_matrix_file(self):
        self.ensure_one()
        file_reader = self.get_file_csv_data(self.fec_file)
        matrix_file_reader = self.get_file_csv_data(self.matrix_tiers_file)
        self.partner_ids = self.get_partner_lines(file_reader, matrix_file_reader)
        self.state = 'validate_partners'
        ACTION['res_id'] = self.id
        return ACTION

    def get_value_from_data(self, data, key, value):
        for line in data:
            if line[key] == value:
                return line
        return False

    def get_config_from_code(self, value):
        config_ids = self.env['ci.account.import.fec.config'].search([])
        value = self._get_encoded_sc(value)
        for config in config_ids:
            start_code = self._get_encoded_sc(config.start_code)
            end_code = self._get_encoded_ec(config.end_code)
            if start_code <= value and end_code >= value:
                return config
        return False

    def _get_encoded_sc(self, code, limit=10):
        if len(str(code)) < limit:
            len_code = 10 - len(str(code))
            chaine = ""
            # for x in xrange(len_code):
            chaine = chaine + "0" * len_code
            return int(str(code) + chaine)

    def _get_encoded_ec(self, code, limit=10):
        if len(str(code)) < limit:
            len_code = 10 - len(str(code))
            chaine = ""
            # for x in xrange(len_code):
            chaine = chaine + "9" * len_code
            return int(str(code) + chaine)

    @api.multi
    def _filter_data(self, data):
        self.ensure_one()
        journal_codes = set(list(map(lambda row: row['JournalCode'], data)))
        logging.info("**************** Debut Verification Avant Import ****************")
        self.verify_journal(data)
        self.verify_account(data)
        self._verif_assert_balanced(data)
        logging.info("**************** Fin Verification Avant Import ****************")
        if journal_codes:
            for index, row in enumerate(data):
                if row['JournalCode'] not in journal_codes:
                    del data[index]
        return True

    @api.multi
    def verify_journal(self, data):
        self.ensure_one()
        journal_codes = set(list(map(lambda row: row['JournalCode'], data)))
        return self._verify_data(journal_code=journal_codes)

    @api.multi
    def verify_account(self, data):
        self.ensure_one()
        account_codes = set(list(map(lambda row: row['CompteNum'], data)))
        return self._verify_data(account_code=account_codes)

    @api.model
    def _verify_data(self, journal_code=False, account_code=False):
        message = ""
        journal_codes = []
        account_codes = []
        if journal_code:
            logging.info("**************** DEBUT Verification Journaux ****************")
            for x in journal_code:
                line_id = self.env['ci.account.import.fec.line'].search([('journal_code_src', '=', x)])
                if not line_id or not line_id.journal_code_dst.code:
                    journal_codes.append(line_id.journal_code_src)
            logging.info("**************** FIN Verification Journaux ****************")
        if account_code:
            logging.info("**************** DEBUT Verification Comptes ****************")
            for y in account_code:
                account_line_id = self.env['ci.account.import.fec.compte'].search([('compte_src', '=', y)])
                if not account_line_id or not account_line_id.compte_dst.code:
                    account_codes.append(account_line_id.compte_src)
            logging.info("**************** FIN Verification Comptes ****************")

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
    def _import_data(self, data):
        precision = self.env.user.company_id.currency_id.decimal_places
        move_obj = self.env['account.move']
        moves = []
        move_ids = []
        logging.info("**************** Debut Import ****************")
        if self.import_auto_num:
            logging.info("---- Ecritures Auto ---- %s", data)

            for ecritureNum, lines_jrl in groupby(data, lambda l: l['EcritureNum']):
                lines_jrl = list(lines_jrl)
                logging.info("---- By Journals - %s ---- %s", ecritureNum, lines_jrl)
                for pieceDate, lines_date in groupby(lines_jrl, lambda l: l['PieceDate']):
                    lines_date = list(lines_date)
                    debit = 0
                    credit = 0
                    lines = []
                    logging.info("---- By Date - %s ---- %s", pieceDate, lines_date)
                    for line in lines_date:
                        debit_src = float_round(float(line['Debit'].replace(',', '.')), precision_digits=precision)
                        credit_src = float_round(float(line['Credit'].replace(',', '.')), precision_digits=precision)
                        debit = float_round(debit, precision_digits=precision) + debit_src
                        credit = float_round(credit, precision_digits=precision) + credit_src
                        # logging.info("---- debit = %s - credit = %s ----", debit, credit)
                        lines.append(line)
                        if debit == credit:
                            # logging.info("---------- Import value : %s", lines)
                            vals = self.get_move_account(lines)
                            move = move_obj.create(vals)
                            logging.info("---------- Import : %s Success", move)
                            moves.append(move)
                            debit = 0
                            credit = 0
                            lines = []

        else:
            logging.info("---- Ecritures Manuelles ----")
            for ecritureNum, lines in groupby(data, lambda l: l['EcritureNum']):
                lines = list(lines)
                vals = self.get_move_account(lines)
                move = move_obj.create(vals)
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

    @api.multi
    def trans_rec_reconcile_full(self, line_ids):
        move_lines = self.env['account.move.line'].search([('id', 'in', line_ids)])
        # Don't consider entrires that are already reconciled
        move_lines_filtered = move_lines.filtered(lambda aml: not aml.reconciled)
        logging.info('-- 1 - %s', move_lines_filtered)
        # Because we are making a full reconcilition in batch, we need to consider use cases as defined in the test test_manual_reconcile_wizard_opw678153
        # So we force the reconciliation in company currency only at first
        move_lines_filtered.with_context(skip_full_reconcile_check='amount_currency_excluded').reconcile()
        logging.info('-- 2 -  %s', move_lines_filtered)
        # then in second pass, consider the amounts in secondary currency (only if some lines are still not fully reconciled)
        move_lines.force_full_reconcile()
        logging.info('-- 3 -  %s', move_lines_filtered)
        return True

    @api.model
    def _reconcile(self, move_ids):
        if move_ids:
            logging.info("---------- move_ids.mapped %s", move_ids)
            move__vals = []
            # for move_id in move_ids:
            line_obj = self.env['account.move.line']
            lines_to_reconcile = line_obj.search([('is_reconcile_mapping', '=', True),
                                                  ('account_id.reconcile', '=', True),
                                                  ('fec_reconcile_mapping', '=', 'Z'),
                                                  ('move_id', 'in', move_ids)])

            lines_to_reconcile = lines_to_reconcile.sorted(
                key=lambda p: p.fec_reconcile_mapping,
                reverse=True,
            )

            for code_mapping, move_lines in groupby(lines_to_reconcile, lambda l: l.fec_reconcile_mapping):
                move_lines = list(move_lines)
                line_ids = []
                if code_mapping != 'Z':
                    for line in move_lines:
                        line_ids.append(line.id)
                    logging.info("---------- Lettrage : %s - %s Success", code_mapping, line_ids)

                    self.trans_rec_reconcile_full(line_ids)

                # if lines_to_reconcile:
                #     for line in lines_to_reconcile:
                #         if line.is_reconcile_mapping and line.fec_reconcile_mapping:
                #             reconcile_id = self.env['account.full.reconcile'].search(
                #                 [('name', '=', line.fec_reconcile_mapping)])
                #             if not reconcile_id:
                #                 reconcile_id = self.env['account.full.reconcile'].create(
                #                     {'name': line.fec_reconcile_mapping})
                #             line.write({
                #                 'full_reconcile_id': reconcile_id.id
                #             })
            # logging.info("---------- Lettrage : %s Success", line)
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
                account_id = self._get_account_from_line(line['CompteNum'], line['CompAuxNum'])
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
            # if self.import_auto_num:
            #     move_vals['name'] = self.env['ir.sequence'].next_by_code('mrp.routing')
            if not self.import_auto_num:
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
    def _get_journal_from_line(self, code):
        line_id = self.env['ci.account.import.fec.line'].search([('journal_code_src', '=', code)])
        if line_id and line_id.journal_code_dst.code:
            return line_id.journal_code_dst.code
        raise exceptions.Warning(_("The line %s is not mapped with a journal code!") % code)

    @api.model
    def _get_account_from_line(self, code, partner=False):
        line_id = self.env['ci.account.import.fec.compte'].search([('compte_src', '=', code)])
        if line_id:
            if partner:
                partner_id = self.env['ci.account.import.fec.partner'].search([('partner_src', '=', partner)])
                if partner_id.partner_dst:
                    if partner_id.type == 'C':
                        return partner_id.partner_dst.property_account_receivable_id.code
                    elif partner_id.type == 'F':
                        return partner_id.partner_dst.property_account_payable_id.code

            if line_id.compte_dst.code:
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
            # raise exceptions.Warning(_("The %s %%s doesn't exist" % self.env[model]._description) % code)
            return False
        return records[code]

    @api.model
    def _get_amount(self, value, sign=False):
        amount = eval(value.replace(',', '.') or '0.0')
        return amount if sign else abs(amount)

    @api.model
    def _get_date(self, date):
        return '%s-%s-%s' % (date[:4], date[4:6], date[6:])
