import calendar

from django import forms

from employees.models import Employee, Salary


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['FIO', 'position', 'salary', 'address', 'phone_number', 'username', 'password']


def _get_month_name(month_number: int) -> str:
    match month_number:
        case 1: return "Январь"
        case 2: return "Февраль"
        case 3: return "Март"
        case 4: return "Апрель"
        case 5: return "Май"
        case 6: return "Июнь"
        case 7: return "Июль"
        case 8: return "Август"
        case 9: return "Сентябрь"
        case 10: return "Октябрь"
        case 11: return "Ноябрь"
        case 12: return "Декабрь"


class SelectYearMonthForm(forms.Form):
    year_choices = [(None, '----------')] + [(i, i) for i in range(2023, 2101)]
    year = forms.ChoiceField(choices=year_choices, label='Год')

    month_choices = [(None, '----------')] + [(i, _get_month_name(i)) for i in range(1, 13)]
    month = forms.ChoiceField(choices=month_choices, label='Месяц')


class SalaryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SalaryForm, self).__init__(*args, **kwargs)

        self.fields['year'].widget.attrs['readonly'] = True
        self.fields['month'].widget.attrs['readonly'] = True

    class Meta:
        model = Salary
        fields = ['year', 'month', 'employee', 'general']
