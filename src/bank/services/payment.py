import datetime

from django.db import connection

from bank.models import Credit, Payment


class PaymentService:
    # @staticmethod
    # def calculate_payment(date, credit_id: int) -> Payment:
    #     try:
    #         credit = Credit.objects.get(id=credit_id)
    #         last_payment = Payment.objects.filter(credit_id=credit_id)
    #
    #         if last_payment.exists():
    #             last_payment = last_payment.order_by('date').last()
    #             days_overdue: int = _get_overdue(credit.date, date, previous_payment_date=last_payment.date)
    #         else:
    #             days_overdue: int = _get_overdue(credit.date, date)
    #
    #         amount: float = credit.amount / credit.term
    #         percent: float = (credit.amount * (credit.annual_percent / 100)) / 12
    #         general_amount: float = amount + percent
    #         penalties: float = general_amount * credit.penalties / 100 * days_overdue
    #         total: float = general_amount + penalties
    #
    #         if not last_payment:
    #             remains: float = credit.amount - amount
    #         else:
    #             remains: float = last_payment.remains - amount
    #
    #         return Payment(credit_id=credit_id,
    #                        date=date,
    #                        amount=amount,
    #                        percent=percent,
    #                        general_amount=general_amount,
    #                        days_overdue=days_overdue,
    #                        penalties=penalties,
    #                        total=total,
    #                        remains=remains
    #                        )
    #     except Credit.DoesNotExist:
    #         return Payment()

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


def _get_overdue(credit_date, payment_date, /, previous_payment_date=None) -> int:
    assert payment_date >= credit_date, 'Payment date must be greater than or equal to credit date'

    if previous_payment_date is not None:
        credit_date = datetime.date(year=credit_date.year, month=previous_payment_date.month, day=credit_date.day)

    days_difference = (payment_date - credit_date).days
    return days_difference - 30 if days_difference > 30 else 0
