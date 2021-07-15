# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import tools


class WarehousePosBranchReport(models.Model):
    _name = 'pos.warehouse.branch.report'
    _description = "Pos Warehouse Branch Report"
    _rec_name = 'id'
    _auto = False

    product_id = fields.Many2one('product.product', 'Product')
    categ_id = fields.Many2one('product.category', 'Product Category')
    location_id = fields.Many2one('stock.location', 'Location')
    pos_branch_id = fields.Many2one('pos.branch', 'Branch')

    quantity = fields.Float('Quantity')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        concat1 = '%/'
        concat2 = '/%'

        select_ = """
                min(s.id) as id,
                s.product_id as product_id,
                pt.categ_id AS categ_id,
                s.location_id as location_id,
                pb.id as pos_branch_id,
                s.quantity as quantity
            """

        for field in fields.values():
            select_ += field

        from_ = """
                stock_quant s
                LEFT JOIN product_product pp ON pp.id = s.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                INNER JOIN product_category cat ON pt.categ_id = cat.id
                JOIN stock_location ls on (s.location_id=ls.id and ls.usage = 'internal' and ls.active='true')
                JOIN stock_warehouse whs ON ls.parent_path like concat('%s', whs.view_location_id, '%s')
                JOIN pos_branch pb on  whs.pos_branch_id = pb.id %s
            """ % (concat1, concat2, from_clause)

        groupby_ = """
                s.product_id,
                pt.categ_id,
                s.location_id,
                pb.id,
                s.quantity %s
            """ % groupby

        return '%s (SELECT %s FROM %s WHERE s.id IS NOT NULL GROUP BY %s )' % (with_, select_, from_, groupby_)
