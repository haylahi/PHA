# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = "account.account"

    def _compute_move_lines(self):
        for rec in self:
            credit = debit = balance = 0
            for move_line in rec.move_line_ids:
                credit += move_line.credit
                debit += move_line.debit
                balance += move_line.balance
            rec.debit= debit
            rec.credit = credit
            rec.balance = balance

    move_line_ids = fields.One2many('account.move.line', 'account_id', string='Move lines',)
    debit = fields.Float(compute='_compute_move_lines')
    credit = fields.Float(compute='_compute_move_lines')
    balance = fields.Float(compute='_compute_move_lines')