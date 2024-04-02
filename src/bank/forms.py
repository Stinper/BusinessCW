import datetime

from django import forms
from bank.models import Payment, Credit


class CreditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)

        self.fields['annual_percent'].widget.attrs['readonly'] = True
        self.fields['penalties'].widget.attrs['readonly'] = True
        self.fields['date'].widget.attrs['readonly'] = True

    date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
        initial=datetime.date.today().strftime('%Y-%m-%d'),
    )

    class Meta:
        model = Credit
        fields = ['amount', 'term', 'annual_percent', 'penalties', 'date']


class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['percent'].widget.attrs['readonly'] = True
        self.fields['general_amount'].widget.attrs['readonly'] = True
        self.fields['days_overdue'].widget.attrs['readonly'] = True
        self.fields['penalties'].widget.attrs['readonly'] = True
        self.fields['total'].widget.attrs['readonly'] = True
        self.fields['remains'].widget.attrs['readonly'] = True

    date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
        initial=datetime.date.today().strftime('%Y-%m-%d'),
    )

    class Meta:
        model = Payment
        fields = ['date', 'amount', 'percent', 'general_amount',
                  'days_overdue', 'penalties', 'total', 'remains']
