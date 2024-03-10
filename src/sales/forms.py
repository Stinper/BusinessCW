from django import forms

from sales.models import Sale


class SalesForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'
        exclude = ['sum']
