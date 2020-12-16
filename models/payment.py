# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import requests
import pprint
from requests.exceptions import HTTPError
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_stripe.controllers.main import StripeController

_logger = logging.getLogger(__name__)

# The following currencies are integer only, see https://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYG', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
]

class PaymentAcquirerStripe(models.Model):
    _inherit = 'payment.acquirer'

    def stripe_token_from_payment(self, data):
        # create payment_method
        s2s_data_payment_method = {
            'type': 'card',
            'card[number]': data.get('number'),
            'card[cvc]': data.get('cvc'),
            'card[exp_month]': data.get('exp_month'),
            'card[exp_year]': data.get('exp_year'),
        }
        payment_method = self._stripe_request('payment_methods', s2s_data_payment_method)

        # create customer
        s2s_data_customer = {
            'email': self.env.user.partner_id.email
        }
        customer = self._stripe_request('customers', s2s_data_customer)

        # link customer with payment method
        api_url_payment_method = 'payment_methods/%s/attach' % payment_method.get('id')
        method_data = {
            'customer': customer.get('id')
        }
        self._stripe_request(api_url_payment_method, method_data)
        
        # create payment.token
        s2s_data_token = {
            'customer': customer.get('id'),
            'payment_method': payment_method.get('id'),
            'card': payment_method.get('card'),
            'acquirer_id': self.id,
            'partner_id': self.env.user.partner_id.id
        }
        token = self.stripe_s2s_form_process(s2s_data_token)

        return token.id


    