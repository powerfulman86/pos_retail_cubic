# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    pos_branch_id = fields.Many2one(
        'pos.branch',
        string='Branch',
    )

    @api.model
    def create(self, vals):
        if not vals.get('pos_branch_id'):
            vals.update({'pos_branch_id': self.env['pos.branch'].sudo().get_default_branch()})
        warehouse = super(StockWarehouse, self).create(vals)
        return warehouse

    warehouse_product_ids = fields.One2many('stock.quant', 'location_id', string='Available Products',
                                            compute='compute_warehouse_products')

    def compute_warehouse_products(self):
        for products in self:
            warehouse_all_products = self.env['stock.quant'].search([('location_id', 'child_of', self.code)])
            if warehouse_all_products:
                for i in warehouse_all_products:
                    products.warehouse_product_ids = warehouse_all_products
            else:
                products.warehouse_product_ids = False


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    categ_id = fields.Many2one(related='product_id.categ_id')


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    pos_branch_id = fields.Many2one(
        'pos.branch',
        related='warehouse_id.pos_branch_id',
        store=True,
        readonly=1
    )
