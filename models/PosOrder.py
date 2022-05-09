# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, registry
from odoo.tools import float_is_zero


class POSOrder(models.Model):
    _inherit = 'pos.order'

    extra_discount_total = fields.Float(string='Extra Discount', default='0', store=True,
                                        compute="_compute_extra_discount_total")

    @api.depends('lines.extra_discount_value')
    def _compute_extra_discount_total(self):
        for order in self:
            order.extra_discount_total = sum(order.mapped('lines.extra_discount_value'))

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(POSOrder, self)._order_fields(ui_order)
        if ui_order.get('picking_type_id', None):
            order_fields.update({
                'picking_type_id': ui_order['picking_type_id']
            })
        else:
            order_fields.update({
                'picking_type_id': self.env['pos.session'].browse(
                    ui_order.get('pos_session_id')).config_id.picking_type_id.id
            })
        if ui_order.get('add_credit', False):
            order_fields.update({
                'add_credit': ui_order['add_credit']
            })
        if ui_order.get('medical_insurance_id', False):
            order_fields.update({
                'medical_insurance_id': ui_order['medical_insurance_id']
            })
        if ui_order.get('partial_payment', False):
            order_fields.update({
                'partial_payment': ui_order['partial_payment']
            })
        if ui_order.get('sale_id', False):
            order_fields.update({
                'sale_id': ui_order['sale_id']
            })
        if ui_order.get('delivery_date', False):
            order_fields.update({
                'delivery_date': ui_order['delivery_date']
            })
        if ui_order.get('delivery_address', False):
            order_fields.update({
                'delivery_address': ui_order['delivery_address']
            })
        if ui_order.get('parent_id', False):
            order_fields.update({
                'parent_id': ui_order['parent_id']
            })
        if ui_order.get('sale_journal', False):
            order_fields['sale_journal'] = ui_order.get('sale_journal')
        if ui_order.get('ean13', False):
            order_fields.update({
                'ean13': ui_order['ean13']
            })
        if ui_order.get('expire_date', False):
            order_fields.update({
                'expire_date': ui_order['expire_date']
            })
        if ui_order.get('is_return', False):
            order_fields.update({
                'is_return': ui_order['is_return']
            })
        if ui_order.get('email', False):
            order_fields.update({
                'email': ui_order.get('email')
            })
        if ui_order.get('email_invoice', False):
            order_fields.update({
                'email_invoice': ui_order.get('email_invoice')
            })
        if ui_order.get('plus_point', 0):
            order_fields.update({
                'plus_point': ui_order['plus_point']
            })
        if ui_order.get('redeem_point', 0):
            order_fields.update({
                'redeem_point': ui_order['redeem_point']
            })
        if ui_order.get('note', None):
            order_fields.update({
                'note': ui_order['note']
            })
        if ui_order.get('return_order_id', False):
            order_fields.update({
                'return_order_id': ui_order['return_order_id']
            })
        if ui_order.get('location_id', False):
            order_fields.update({
                'location_id': ui_order['location_id']
            })
        if ui_order.get('booking_id', False):
            order_fields.update({
                'booking_id': ui_order['booking_id']
            })
        if ui_order.get('currency_id', False):
            order_fields.update({
                'currency_id': ui_order['currency_id']
            })
        if ui_order.get('analytic_account_id', False):
            order_fields.update({
                'analytic_account_id': ui_order['analytic_account_id']
            })
        if ui_order.get('combo_item_ids', False):
            order_fields.update({
                'combo_item_ids': ui_order['combo_item_ids']
            })
        if ui_order.get('shipping_id'):
            order_fields.update({
                'shipping_id': ui_order['shipping_id']
            })
        if ui_order.get('extra_discount_total'):
            order_fields.update({
                'extra_discount_total': ui_order['extra_discount_total']
            })
        return order_fields

    def _cron_fix_missing_analytic(self):
        pos_orders = self.env['pos.order'].search([('analytic_account_id', '=', False)], limit=1000)

        for rec in pos_orders:
            if rec.session_id.config_id.analytic_account_id:
                rec.analytic_account_id = rec.session_id.config_id.analytic_account_id

    def create_picking_bundle_pack(self, combo_item_dict):
        if combo_item_dict:
            warehouse_obj = self.env['stock.warehouse']
            move_object = self.env['stock.move']
            moves = move_object
            picking_obj = self.env['stock.picking']
            picking_type = self.picking_type_id
            location_id = self.location_id.id
            if self.partner_id:
                destination_id = self.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = warehouse_obj._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id
            is_return = self.is_return
            picking_vals = {
                'is_picking_combo': True,
                'user_id': False,
                'origin': self.pos_reference,
                'partner_id': self.partner_id.id if self.partner_id else None,
                'date_done': self.date_order,
                'picking_type_id': picking_type.id,
                'company_id': self.company_id.id,
                'move_type': 'direct',
                'note': self.note or "",
                'location_id': location_id if not is_return else destination_id,
                'location_dest_id': destination_id if not is_return else location_id,
                'pos_order_id': self.id,
            }
            picking_combo = picking_obj.create(picking_vals)
            for combo_item_id, product_uom_qty in combo_item_dict.items():
                combo_item = self.env['pos.combo.item'].browse(combo_item_id)
                product = combo_item.product_id
                vals = {
                    'name': self.name,
                    'combo_item_id': combo_item.id,
                    'product_uom': product.uom_id.id,
                    'picking_id': picking_combo.id,
                    'picking_type_id': picking_type.id,
                    'product_id': product.id,
                    'product_uom_qty': product_uom_qty,
                    'state': 'draft',
                    'location_id': location_id if not is_return else destination_id,
                    'location_dest_id': destination_id if not is_return else location_id,
                }
                move = move_object.create(vals)
                moves |= move
            self.write({'picking_id': picking_combo.id})
            self._force_picking_done(picking_combo)
        return True

    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        # If no email is set on the user, the picking creation and validation will fail be cause of
        # the 'Unable to log message, please configure the sender's email address.' error.
        # We disable the tracking in this case.
        if not self.env.user.partner_id.email:
            Picking = Picking.with_context(tracking_disable=True)
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = picking_type.default_location_src_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if not order.picking_id:
                if picking_type:
                    message = _(
                        "This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                                  order.id, order.name)
                    picking_vals = {
                        'origin': '%s - %s' % (order.session_id.name, order.name),
                        'partner_id': address.get('delivery', False),
                        'user_id': False,
                        'date_done': order.date_order,
                        'picking_type_id': picking_type.id,
                        'company_id': order.company_id.id,
                        'move_type': 'direct',
                        'note': order.note or "",
                        'location_id': location_id,
                        'location_dest_id': destination_id,
                    }
                    pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                    if pos_qty:
                        order_picking = Picking.create(picking_vals.copy())
                        if self.env.user.partner_id.email:
                            order_picking.message_post(body=message)
                        else:
                            order_picking.sudo().message_post(body=message)
                    neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                    if neg_qty:
                        return_vals = picking_vals.copy()
                        return_vals.update({
                            'location_id': destination_id,
                            'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                            'picking_type_id': return_pick_type.id
                        })
                        return_picking = Picking.create(return_vals)
                        if self.env.user.partner_id.email:
                            return_picking.message_post(body=message)
                        else:
                            return_picking.sudo().message_post(body=message)
            else:
                order_picking = order.picking_id
            for line in order.lines.filtered(
                    lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                              precision_rounding=l.product_id.uom_id.rounding)):
                moves |= Move.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })

            # prefer associating the regular order picking, not the return
            if not self.picking_id:
                order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)

            # when the pos.config has no picking_type_id set only the moves will be created
            if moves and not return_picking and not order_picking:
                moves._action_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()

        return True
