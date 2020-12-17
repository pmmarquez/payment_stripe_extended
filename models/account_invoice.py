# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tests import Form
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re


from datetime import date, timedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    def stripe_pay_invoice(self, payment_token_id):
        payment_token = self.env['payment.token'].browse(payment_token_id)
        action = self.action_invoice_register_payment()
        # .with_user(SUPERUSER_ID)
        payment_form = Form(self.env['account.payment'].with_context(action['context']), view='account.view_account_payment_invoice_form')
        payment_form._values['journal_id'] = payment_token.acquirer_id.journal_id.id
        for payment_method in payment_token.acquirer_id.journal_id.inbound_payment_method_ids :
            if payment_method.code == 'electronic':
                payment_form._values['payment_method_id'] = payment_method.id
                payment_form._values['payment_method_code'] = 'electronic'
        payment_form._values['payment_token_id'] = payment_token.id
        payment = payment_form.save()
        payment.post()
        return payment.payment_transaction_id.id
