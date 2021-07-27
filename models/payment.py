# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    visa = fields.Boolean('Visa')

    @api.onchange('is_cash_count', 'visa')
    @api.constrains('is_cash_count', 'visa')
    def change_cash_visa(self):
        if self.is_cash_count is True and self.visa is True:
            raise ValidationError(_("Select Cash Or Visa NO Both "))
