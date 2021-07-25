# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosSaleReport(models.TransientModel):
    _inherit = 'pos.sale.report'
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    config_ids = fields.Many2many('pos.config', compute='_get_current_user')

    @api.depends('report_type')
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
            rec.config_ids = [(6, 0, [self.env.user.pos_config_id.id])] if self.env.user.pos_config_id else [(6, 0, [])]
            if self.env.user.has_group('pos_retail.group_branch_manager') or \
                    self.env.user.has_group('pos_retail.group_pos_report') or \
                    self.env.user.has_group('point_of_sale.group_pos_manager'):
                rec.config_ids = [(6, 0, self.env['pos.config'].search([]).ids)]


class PosConfig(models.Model):
    _inherit = 'pos.config'

    modify_bom = fields.Boolean(string='Modify BOM')
    cash_balance = fields.Boolean(string='Cash Register Balance')
    show_mrp_order = fields.Boolean(string='Show MRP Order')
    hide_mrp_produce_direct = fields.Boolean(string='Hid Mrp Button')


    @api.onchange('mrp')
    def onchange_mrp2(self):
        if not self.mrp:
            self.modify_bom = False
