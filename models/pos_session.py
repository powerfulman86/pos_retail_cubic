# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError


# _logger = logging.getLogger(__name__)
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
