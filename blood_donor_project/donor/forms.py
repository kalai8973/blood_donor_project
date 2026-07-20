from django import forms
from .models import Donor, BloodRequest


class DonorForm(forms.ModelForm):

    class Meta:
        model = Donor
        fields = '__all__'


class BloodRequestForm(forms.ModelForm):

    class Meta:
        model = BloodRequest
        fields = '__all__'