# coding: utf-8
import time
from odoo import fields, models


class L10nUt(models.Model):
    _name = 'l10n.ut'
    _description = 'Tax Unit'
    _order = 'date desc'

    name = fields.Char(string='Reference number', size=64, required=True, readonly=False, default=None,
                       help="Reference number under the law")

    date = fields.Date(string='Date', required=True,
                       help="Date on which goes into effect the new Unit Tax Unit")

    amount = fields.Float(string='Amount', digits='Amount Bs per UT',
                          help="Amount of the tax unit in bs", required=True)

    user_id = fields.Many2one('res.users', string='Salesman', readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda s: s._uid, help="Vendor user")

    def get_amount_ut(self, date=False):
        # Return the value of the tributary uom of the specified date or if it's empty return the value to current date.
        rate = 0
        date = date or time.strftime('%Y-%m-%d')
        self._cr.execute("""SELECT amount FROM l10n_ut WHERE date <= '%s'
                   ORDER BY date desc LIMIT 1""" % date)
        if self._cr.rowcount:
            rate = self._cr.fetchall()[0][0]
        return rate

    def compute(self, from_amount, date=False, context=None):
        # Return the number of tributary units depending on an amount of money.
        result = 0.0
        ut = self.get_amount_ut(date=date)
        if ut:
            result = from_amount / ut
        return result

    def compute_ut_to_money(self, amount_ut, date=False, context=None):
        # Transforms from tax units into money
        money = 0.0
        ut = self.get_amount_ut(date)
        if ut:
            money = amount_ut * ut
        return money

    def exchange(self, from_amount, from_currency_id, to_currency_id, exchange_date, context=None):
        if from_currency_id == to_currency_id:
            return from_amount
        rc_obj = self.env['res.currency']
        fci = rc_obj.browse(from_currency_id)
        tci = rc_obj.browse(to_currency_id)
        return rc_obj._compute(fci, tci, from_amount)

    def sxc(self, from_currency_id, to_currency_id, exchange_date, context=None):
        # This is a closure that allow to use the exchange rate conversion in a short way
        def _xc(from_amount):
            return self.exchange(from_amount, from_currency_id, to_currency_id, exchange_date)
        return _xc
