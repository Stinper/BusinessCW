from  django import forms

from products.models import Product


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.fields['amount'].initial = 0
        self.fields['sum'].initial = 0

        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['sum'].widget.attrs['readonly'] = True

    class Meta:
        model = Product
        fields = '__all__'
