from django import forms


__all__ = [
    'DateRangeForm'
]


class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Начальная дата', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Конечная дата', widget=forms.DateInput(attrs={'type': 'date'}))
