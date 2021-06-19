# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api


class pos_sale_analytic(models.Model):
    _inherit = 'pos.sale.analytic'

    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    discount_total = fields.Float(string='Discount Total', readonly=True)
    discount_extra = fields.Float(string='Discount Extra', readonly=True)

    def _pos_order_select(self):
        select = """SELECT min(pol.id) AS id,
            po.name as name,
            po.user_id as user_id,
            po.date_order AS date,
            po.pos_branch_id AS pos_branch_id,
            pol.product_id AS product_id,
            pt.categ_id AS product_categ_id,
            pt.pos_categ_id AS pos_categ_id,
            pp.product_tmpl_id AS product_tmpl_id,
            po.company_id AS company_id,
            'Point of Sale' AS origin,
            sum(pol.qty) AS qty,
            sum(pol.discount) as discount_total,
            po.amount_return as discount_extra,
            sum(pol.price_unit * pol.qty - pol.price_unit * pol.qty / 100 * pol.discount) as sale_total
            FROM pos_order_line pol
            LEFT JOIN pos_order po ON po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE po.state IN ('paid', 'done', 'invoiced')
            GROUP BY po.name,
                po.date_order,
                po.pos_branch_id,
                pol.product_id,
                pp.product_tmpl_id,
                po.company_id,
                pt.categ_id, 
                pt.pos_categ_id, 
                po.user_id,
                po.amount_return
        """
        return select

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("CREATE OR REPLACE VIEW %s AS %s" % (self._table, self._pos_order_select()))
