# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tests import Form
from odoo.tools.float_utils import float_round

from datetime import date, timedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    def cliente_stripe_pay_invoice(self, payment_token_id):
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

    def pay_vendor_invoice(self):
        payment_stripe = self.env['payment.acquirer'].search([('provider', '=', 'stripe')])
        action = self.action_invoice_register_payment()
        # .with_user(SUPERUSER_ID)
        payment_form = Form(self.env['account.payment'].with_context(action['context']), view='account.view_account_payment_invoice_form')
        purchase_order = self.env['purchase.order'].search([('name','ilike',self.invoice_origin)])
        client_invoice = self.env['account.move'].search([('invoice_origin','ilike',purchase_order.origin)])
        # stripe transfer
        # self.amount_tota
        s2s_data_transfer = {
            "amount": int(float_round(40.00 * 100, 2)),
            "currency": self.currency_id.name,
            "destination": self.partner_id.stripe_connect_account_id,
            "transfer_group": self.env['payment.transaction'].search([('id','=',client_invoice.transaction_ids.id)]).reference,
        }
        transfer = payment_stripe._stripe_request('transfers', s2s_data_transfer)
        # return transfer info
        if transfer.get('id'):
            payment = payment_form.save()
            payment.post()
            
            return_transaction_info = {
                'odoo_payment_id':payment.id,
                'stripe_transfer_id': transfer.get('id')
            }

            self.env['bus.bus'].sendone(
                self._cr.dbname + '_' + str(self.partner_id.id),
                {'type': 'stripe_transfer_vendor_notification', 'action':'created', "transaction_info":return_transaction_info})
            return return_transaction_info
        else:
            return False
