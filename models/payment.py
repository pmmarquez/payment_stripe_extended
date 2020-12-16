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

    def _message_post_process_attachments(self, attachments, attachment_ids, message_values):
        new_attachments = []
        if attachments:
            for attachment in attachments:
                if len(attachment) == 2 or len(attachment) == 3:
                    if isinstance(attachment[1], xmlrpclib.Binary):
                        attachment[1] = bytes(attachment[1].data)
                new_attachments.append(attachment)
            attachments = new_attachments
        return super(MailThread, self)._message_post_process_attachments(attachments, attachment_ids, message_values)

    