# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, registry


class ResUsers(models.Model):
    _inherit = 'res.users'

    area_branch_ids = fields.Many2many('pos.branch', compute="_compute_area_branch")

    @api.depends('name')
    def _compute_area_branch(self):
        for rec in self:
            branches = []
            area_ids = self.env['res.area'].search([('user_id', '=', rec.id)])
            for area in area_ids:
                for branch in area.branch_ids:
                    branches.append(branch.id)
            rec.area_branch_ids = [(6, 0, branches)]


