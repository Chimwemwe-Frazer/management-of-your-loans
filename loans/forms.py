from django.contrib.auth.forms import AuthenticationForm
from django import forms

class StyledAuthenticationForm(AuthenticationForm):
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
