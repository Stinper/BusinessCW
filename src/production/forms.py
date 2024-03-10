from django import forms

from production.models import Production


class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = '__all__'
