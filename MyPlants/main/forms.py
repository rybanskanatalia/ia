from django import forms
from .models import Plants, PlantList

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

class ShareListForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super(ShareListForm, self).__init__(*args, **kwargs)
        if user:
            # Filter the queryset to include only the user's lists
            self.fields['list'].queryset = PlantList.objects.filter(userID=user)

    list = forms.ModelChoiceField(queryset=PlantList.objects.none(), empty_label=None, label='Select a list')
    email = forms.EmailField(label='Who are you sharing with (email)')