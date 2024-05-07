from django.db import connection

__all__ = [
    'SalaryService'
]


class SalaryService:
    @staticmethod
    def get_salary_list(year: int, month: int):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_salary_list(%(year)s, %(month)s)",
                           {
                               'year': year,
                               'month': month
                           })

            return cursor.fetchall()

    @staticmethod
    def get_salary_list_between_dates(date_from: str, date_to: str):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_salary_list_between_dates(%(date_from)s, %(date_to)s)",
                           {
                               'date_from': date_from,
                               'date_to': date_to
                           })

            return cursor.fetchall()

    @staticmethod
    def get_salary_total_sum(year: int, month: int) -> int:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_salary_total_sum(%(year)s, %(month)s)",
                           {
                               'year': year,
                               'month': month
                           })

            return cursor.fetchall()[0][0]

    @staticmethod
    def create_salary_list(year: int, month: int):
        with connection.cursor() as cursor:
            cursor.execute("CALL create_salary_list(%(year)s, %(month)s)",
                           {
                               'year': year,
                               'month': month
                           })

    @staticmethod
    def issue_salary_to_all_employees(year: int, month: int):
        with connection.cursor() as cursor:
            cursor.execute("CALL issue_salary_to_all_employees(%(year)s, %(month)s)",
                           {
                               'year': year,
                               'month': month
                           })

    @staticmethod
    def is_issued(salary_list) -> bool:
        for salary in salary_list:
            if not salary[11]:
                return False

        return True
