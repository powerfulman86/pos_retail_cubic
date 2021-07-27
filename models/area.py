# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosBranch(models.Model):
    _inherit = 'pos.branch'
    area_id = fields.Many2one('res.area')


class ResArea(models.Model):
    _name = 'res.area'

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users')
    branch_ids = fields.One2many(comodel_name='pos.branch', inverse_name='area_id', )
