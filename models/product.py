# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('is_combo','type')
    def _check_combo_is_service(self):
        if self.is_combo and self.type != 'service':
            raise UserError(_('Error, Combo Product Must Be Of Type Service'))

