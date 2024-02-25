from django import forms
from .models import Plants, PlantList
from django_select2.forms import ModelSelect2Widget

class AddForm(forms.Form):
    plant_autocomplete = forms.ModelChoiceField(
        queryset=Plants.objects.all(),
        widget=ModelSelect2Widget(
            model=Plants,
            search_fields=['name__icontains'],
        )
    )

class CreateNewList(forms.Form):
    location = forms.CharField(label="Location", max_length=200)
    plants = forms.ModelMultipleChoiceField(
        queryset=Plants.objects.none(),  # Update to empty queryset initially
        label="Select Plants",
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, user=None, *args, **kwargs):
        super(CreateNewList, self).__init__(*args, **kwargs)
        if user:
            self.fields['plants'].queryset = Plants.objects.filter(listID__userID=user)

    def save(self, user):
        location = self.cleaned_data['location']
        selected_plants = self.cleaned_data['plants']
        
        # Create the new list
        new_list = PlantList.objects.create(userID=user, location=location, plantAmount=len(selected_plants))
        
        # Add selected plants to the new list
        new_list.plants.add(*selected_plants)
        
        # Return the new list object
        return new_list
    
class AddPlantForm(forms.ModelForm):
    class Meta:
        model = Plants
        fields = ['name', 'type', 'water', 'period']

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['water'].validators = [waterdays]    
        self.fields['period'].validators = [perioddays]

# ensure the values will not be negative
def waterdays(water):
    if water < 1:
        raise forms.ValidationError("water value cannot be negative")
    return water 

def perioddays(period):
    if period < 1: 
        raise forms.ValidationError("period value cannot be negative.")
    return period

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
    note = forms.CharField(label='Leave a special note:', max_length=999)