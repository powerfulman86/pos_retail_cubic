from odoo import fields, models, api
# _logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    receivable_account_id = fields.Many2one('account.account',
        string='Intermediary Account',
        required=True,
        domain=['|',('user_type_id.type', '=', 'Bank and Cash'),('reconcile', '=', True),('user_type_id.type', '=', 'receivable')],
        ondelete='restrict',
        default=False,
        help='Account used as counterpart of the income account in the accounting entry representing the pos sales.')


class POSOrderLine(models.Model):
    _inherit = "pos.order.line"

    def action_create_mrp_production_direct_from_pos(self, config_id, pos_reference, product_id, quantity, bom_lines):
        Production = self.env['mrp.production'].sudo()

        config = self.env['pos.config'].browse(config_id)
        # _logger.info('Processing Bom Lines {}'.format(bom_lines))
        if bom_lines:
            bom_line = self.env['mrp.bom.line'].sudo().browse(bom_lines[0].get('bom_line').get('id'))
        bom = bom_line.bom_id
        picking_type_id = bom.picking_type_id.id if bom.picking_type_id else Production._get_default_picking_type()
        product = self.env['product.product'].browse(product_id)
        production_vals = {
            'bom_id': bom.id,
            'product_id': product_id,
            'product_qty': quantity,
            'product_tmpl_id': product.product_tmpl_id.id,
            'origin': pos_reference,
            'product_uom_id': product.uom_id.id,
            'user_id': self.env.user.id,
            'company_id': self.env.user.company_id.id,
            'picking_type_id': picking_type_id,
        }
        # _logger.info('Created new Production {}'.format(production_vals))
        mrp_order = self.env['mrp.production'].sudo().create(production_vals)
        for bom_line in bom_lines:
            bom_line_value = bom_line.get('bom_line')
            bom_line_record = self.env['mrp.bom.line'].sudo().browse(bom_line_value.get('id'))
            move_vals = {
                'raw_material_production_id': mrp_order.id,
                'name': mrp_order.name,
                'product_id': bom_line_record.product_id.id,
                'product_uom': bom_line_record.product_uom_id.id,
                'product_uom_qty': bom_line.get('quantity') * quantity,
                'picking_type_id': picking_type_id,
                'location_id': config.stock_location_id.id,
                'location_dest_id': config.stock_location_dest_id.id,
                'company_id': mrp_order.company_id.id,
            }
            self.env['stock.move'].sudo().create(move_vals)
        if config.mrp_auto_confirm:
            mrp_order.action_confirm()
        if config.mrp_auto_assign:
            mrp_order.action_assign()
        if config.mrp_auto_done:
            produce = self.env['mrp.product.produce'].with_context({
                'active_id': mrp_order.id,
                'active_ids': [mrp_order.id]
            }).create({
                'product_id': mrp_order.product_id.id,
                'product_uom_id': mrp_order.product_id.uom_id.id,
                'serial': False,
                'qty_producing': mrp_order.product_qty,
                'production_id': mrp_order.id,
                'consumption': mrp_order.bom_id.consumption
            })
            raw_workorder_line_ids = []
            for move in mrp_order.move_raw_ids:
                raw_workorder_line_ids.append((0, 0, {
                    'move_id': move.id,
                    'product_id': move.product_id.id,
                    'qty_to_consume': move.product_uom_qty,
                    'product_uom_id': move.product_uom.id,
                    'qty_done': move.product_uom_qty,
                    'qty_reserved': move.product_uom_qty
                }))
            produce.raw_workorder_line_ids = raw_workorder_line_ids
            if mrp_order.finished_lot_id:
                produce.finished_lot_id = mrp_order.finished_lot_id
            produce.do_produce()
            mrp_order.button_mark_done()
        # _logger.info('MRP Order created: {}'.format(mrp_order.id))
        return {
            'name': mrp_order.name,
            'state': mrp_order.state,
            'id': mrp_order.id,
            'product_id': product_id
        }

