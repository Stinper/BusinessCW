import datetime

from django.db import connection

from bank.models import Credit, Payment


class PaymentService:
    @staticmethod
    def calculate_payment(date, credit_id: int):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM calculate_payment(%(payment_date)s, %(credit_id)s)",
                           {
                               'payment_date': date,
                               'credit_id': credit_id
                           })
            return cursor.fetchone()
    
    @staticmethod
    def get_payments_list(credit_id: int):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_payments_list(%(credit_id)s)",
                           {
                               'credit_id': credit_id
                           })
            return cursor.fetchall()

    @staticmethod
    def get_payments_list_between_dates(credit_id: int, start_date: str, end_date: str):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, credit_id, payment_date,"
                           " round(amount::numeric, 4) as amount, round(percent::numeric, 4) as percent,"
                           " round(general_amount::numeric, 4) as general_amount, days_overdue,"
                           " penalties, round(total::numeric, 4) as total, remains"
                           " FROM get_payments_list(%(credit_id)s) WHERE payment_date "
                           "BETWEEN %(start_date)s AND %(end_date)s",
                           {
                               'credit_id': credit_id,
                               'start_date': start_date,
                               'end_date': end_date
                           })
            return cursor.fetchall()


def _get_overdue(credit_date, payment_date, /, previous_payment_date=None) -> int:
    assert payment_date >= credit_date, 'Payment date must be greater than or equal to credit date'

    if previous_payment_date is not None:
        credit_date = datetime.date(year=credit_date.year, month=previous_payment_date.month, day=credit_date.day)

    days_difference = (payment_date - credit_date).days
    return days_difference - 30 if days_difference > 30 else 0
