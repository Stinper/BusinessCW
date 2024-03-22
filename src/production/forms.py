import datetime

from django import forms

from production.models import Production


class ProductionForm(forms.ModelForm):
    current_date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today().strftime('%Y-%m-%d'),
    )

    class Meta:
        model = Production
        fields = ['product', 'amount', 'current_date', 'employee']
