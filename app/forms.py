from django import forms

class NumeroForm(forms.Form):
    numero = forms.IntegerField(
        label="Cantidad",
        min_value=0,  # Valor mínimo
        required=True,  # Hace que sea un campo obligatorio
        widget=forms.NumberInput()
    )

class Fecha(forms.Form): 
    fecha = forms.CharField(
        label="Fecha:",
        widget=forms.TextInput(attrs={'placeholder': 'dd-mm-aa'})
    )