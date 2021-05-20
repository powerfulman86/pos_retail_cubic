from odoo import fields, models, api


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    receivable_account_id = fields.Many2one('account.account',
        string='Intermediary Account',
        required=True,
        domain=['|',('user_type_id.type', '=', 'Bank and Cash'),('reconcile', '=', True),('user_type_id.type', '=', 'receivable')],
        ondelete='restrict',
        default=False,
        help='Account used as counterpart of the income account in the accounting entry representing the pos sales.')
