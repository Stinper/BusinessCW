from django import forms

from materials.models import Material


class MaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)

        self.fields['amount'].initial = 0
        self.fields['sum'].initial = 0

        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['sum'].widget.attrs['readonly'] = True

    class Meta:
        model = Material
        fields = '__all__'
