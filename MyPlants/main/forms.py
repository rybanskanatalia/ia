from django import forms
from .models import Plants

def waterdays(water):
    if water < 1:
        raise forms.ValidationError("water value cannot be negative")
    return water
    

def perioddays(period):
    if period < 1: 
        raise forms.ValidationError("period value cannot be negative.")
    return period

class CreateNewList(forms.Form):
    location = forms.CharField(label="name", max_length=200)

class AddPlantForm(forms.ModelForm):
    class Meta:
        model = Plants
        fields = ['name', 'type', 'water', 'period']

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['water'].validators = [waterdays]    
        self.fields['period'].validators = [perioddays]

class EditPlantForm(forms.ModelForm):
    class Meta:
        model = Plants
        fields = ['water', 'period']  # fields to be edited