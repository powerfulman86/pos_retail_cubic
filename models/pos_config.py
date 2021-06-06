# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'
    modify_bom = fields.Boolean(string='Modify BOM')
    cash_balance = fields.Boolean(string='Cash Register Balance')
    show_mrp_order = fields.Boolean(string='Show MRP Order')

    @api.onchange('mrp')
    def onchange_mrp2(self):
        if not self.mrp:
            self.modify_bom = False