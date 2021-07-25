# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api


class pos_sale_analytic(models.Model):
    _inherit = 'pos.sale.analytic'

    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    discount_total = fields.Float(string='Discount Total', readonly=True)
    discount_extra = fields.Float(string='Discount Extra', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=1)

    # WARNING : this code doesn't handle uom conversion for the moment
    def _sale_order_select(self):
        select = """SELECT min(sol.id)*-1 AS id,
            so.name as name,
            so.user_id as user_id,
            so.date_order AS date,
            so.partner_id as partner_id,
            so.pos_branch_id AS pos_branch_id,
            sol.product_id AS product_id,
            pt.categ_id AS product_categ_id,
            pt.pos_categ_id AS pos_categ_id,
            pp.product_tmpl_id AS product_tmpl_id,
            so.company_id AS company_id,
            'Sale Order' AS origin,
            sum(sol.product_uom_qty) AS qty,
            sum(sol.price_total) AS sale_total
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE so.state NOT IN ('draft', 'sent', 'cancel')
            GROUP BY so.name, so.partner_id, so.date_order, so.pos_branch_id, sol.product_id, pp.product_tmpl_id,
            so.company_id, pt.categ_id, pt.pos_categ_id, so.user_id
        """
        return select

    def _pos_order_select(self):
        select = """SELECT min(pol.id) AS id,
            po.name as name,
            po.partner_id as partner_id,
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
            po.extra_discount_total as discount_extra,
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
                po.partner_id,
                po.amount_return,
                po.extra_discount_total
        """
        return select

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("CREATE OR REPLACE VIEW %s AS %s" % (self._table, self._pos_order_select()))
