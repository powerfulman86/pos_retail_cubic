# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    receivable_account_id = fields.Many2one('account.account',
                                            string='Intermediary Account',
                                            required=True,
                                            domain=['|', ('user_type_id.type', '=', 'Bank and Cash'),
                                                    ('reconcile', '=', True), ('user_type_id.type', '=', 'receivable')],
                                            ondelete='restrict',
                                            default=False,
                                            help='Account used as counterpart of the income account in the accounting entry representing the pos sales.')


class PosSession(models.Model):
    _inherit = "pos.session"
    ended = fields.Boolean('ended', compute="compute_end")
    show_visa = fields.Boolean('ended', compute="compute_show_visa")
    show_visa_actual = fields.Boolean('ended', compute="compute_show_visa_actual")
    visa_transaction = fields.Float('Transaction')
    visa_expected = fields.Float('Expected in Visa', compute='compute_visa_expected')
    visa_actual = fields.Float('Actual in Visa')
    visa_differ = fields.Float('Expected in Visa', compute='compute_visa_differ')

    def action_pos_session_closing_control(self):
        res = super(PosSession, self).action_pos_session_closing_control()
        print("XXXXXXXXXXXXXX ",self.config_id.payment_method_ids)
        if self.config_id.payment_method_ids:
            if self.config_id.payment_method_ids[0].visa is True:
                move_id = self.env['account.move'].search([
                    ('pos_session_id', '=', self.id)
                ], limit=1)
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'move_id': move_id.id,
                    'name': 'Visa Debit',
                    'account_id': self.config_id.payment_method_ids[0].profit_loss_account_visa.id,
                    'credit': 0.0 if self.visa_differ > 0 else self.visa_differ,
                    'debit': self.visa_differ if self.visa_differ > 0 else 0,
                })
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'move_id': move_id.id,
                    'name': 'Visa Debit',
                    'account_id': self.config_id.payment_method_ids[0].receivable_account_id.id,
                    'debit': 0.0 if self.visa_differ > 0 else self.visa_differ,
                    'credit': self.visa_differ if self.visa_differ > 0 else 0,
                })

        return res

    def confirm(self):
        pass

    def open_visa_wizard(self):
        if self.visa_actual > 0:
            raise ValidationError(_("Can not Modify Actual In Visa"))
        return {
            'name': _('VISA'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('pos_retail_cubic.visa_view_form').id,
            'res_model': 'pos.session',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": {
                'search_default_config_id': [self.config_id],
                'default_config_id': [self.config_id]}
        }

    def _cron_pos_session(self):
        session_ids = self.env['pos.session'].search([])
        for session in session_ids:
            session.compute_visa_differ()

    @api.depends('visa_expected', 'visa_actual')
    def compute_visa_differ(self):
        for rec in self:
            rec.visa_differ = rec.visa_expected - rec.visa_actual

    @api.depends('name', 'visa_transaction')
    def compute_visa_expected(self):
        for rec in self:
            order_ids = self.env['pos.order'].search([('session_id', '=', rec.id)])
            total = 0
            for order in order_ids:
                for line in order.payment_ids:
                    if line.payment_method_id.visa is True:
                        total += line.amount
            rec.visa_expected = total

    @api.depends('state')
    def compute_show_visa(self):
        for rec in self:
            rec.show_visa = False
            if rec.state not in ['closing_control', 'closed'] or self.env.user.has_group(
                    'point_of_sale.group_pos_manager'):
                rec.show_visa = True

    @api.depends('state')
    def compute_show_visa_actual(self):
        for rec in self:
            rec.show_visa_actual = False
            print(rec.visa_actual, "   XXXX   ", rec.state)
            if rec.visa_actual != 0 or rec.state not in ['new_session', 'opening_control',
                                                         'opened'] or self.env.user.has_group(
                'point_of_sale.group_pos_manager'):
                rec.show_visa_actual = True

    @api.depends('cash_register_balance_end_real')
    def compute_end(self):
        for rec in self:
            rec.ended = False
            if (rec.cash_register_balance_end_real > 0 and rec.state != 'closed') or self.env.user.has_group(
                    'point_of_sale.group_pos_manager'):
                rec.ended = True
            # if self.env.user.has_group('point_of_sale.group_pos_manager'):
            #     rec.ended = False

    def open_cashbox_pos(self):
        self.ensure_one()
        for rec in self:
            # and not self.env.user.has_group('point_of_sale.group_pos_manager')
            if rec.cash_register_balance_end_real > 0:
                raise ValidationError(_("You've already set closing cash , you can't change ."))
        action = self.cash_register_id.open_cashbox_id()
        action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
        action['context']['pos_session_id'] = self.id
        action['context']['default_pos_id'] = self.config_id.id
        return action

    def print_z_report(self):
        if self.ended is not True:
            raise ValidationError(_("Please Set Closing Cash Before Print !"))

        datas = {
            'ids': self._ids,
            'form': self.read()[0],
            'model': 'pos.sale.report'
        }
        datas['form']['session_ids'] = self.id
        return self.env.ref('pos_retail.report_pos_sales_pdf').report_action(self, data=datas)

    def action_pos_session_close(self):
        # Session without cash payment method will not have a cash register.
        # However, there could be other payment methods, thus, session still
        # needs to be validated.
        # if not self.cash_register_id:
        return self._validate_session()

        # if self.cash_control and abs(self.cash_register_difference) > self.config_id.amount_authorized_diff:
        #     # Only pos manager can close statements with cash_register_difference greater than amount_authorized_diff.
        #     # if not self.user_has_groups("point_of_sale.group_pos_manager"):
        #     #     raise UserError(_(
        #     #         "Your ending balance is too different from the theoretical cash closing (%.2f), "
        #     #         "the maximum allowed is: %.2f. You can contact your manager to force it."
        #     #     ) % (self.cash_register_difference, self.config_id.amount_authorized_diff))
        #     # else:
        #     return self._warning_balance_closing()
        # else:
        #     return self._validate_session()
