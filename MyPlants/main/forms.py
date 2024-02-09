from django import forms
from .models import Plants

class CreateNewList(forms.Form):
    name = forms.CharField(label="name", max_length=200)
    check = forms.BooleanField(required=False)

class AddPlantForm(forms.ModelForm):
    class Meta:
        model = Plants
        fields = ['name', 'type', 'water', 'fertilise']

    def waterdays(self):
        water = self.cleaned_data.get('water')
        if water < 1:
            raise forms.ValidationError("water value cannot be negative")
        return water
    
    def perioddays(self):
        fertilise = self.cleaned_data.get('fertilise')
        if fertilise < 1:
            raise forms.ValidationError("fertilise value cannot be negative.")
        return fertilise