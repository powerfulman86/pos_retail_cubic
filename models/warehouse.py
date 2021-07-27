# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    pos_branch_id = fields.Many2one(
        'pos.branch',
        related='warehouse_id.pos_branch_id',
        store=True,
        readonly=1
    )
