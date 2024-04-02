from django.db import connection


class CreditService:
    @staticmethod
    def get_credit_list():
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_credits_list()")
            return cursor.fetchall()
