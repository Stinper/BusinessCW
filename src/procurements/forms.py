from django import forms

from procurements.models import Procurement


class ProcurementForm(forms.ModelForm):
    class Meta:
        model = Procurement
        fields = '__all__'
