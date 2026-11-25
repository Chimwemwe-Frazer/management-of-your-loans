from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Borrower

class StyledAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Invalid username or password. Usernames are case-sensitive.',
    }

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 bg-[#06262d] text-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400',
            'autocomplete': 'off',
            'spellcheck': 'false',
            'autocorrect': 'off',
            'autocapitalize': 'off',
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 bg-[#06262d] text-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400',
            'autocomplete': 'off',
            'spellcheck': 'false',
            
        })
    )


class BorrowerDocumentsForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = ("national_id_image", "residence_map_image")
        labels = {
            "national_id_image": "National ID",
            "residence_map_image": "Residence map",
        }
