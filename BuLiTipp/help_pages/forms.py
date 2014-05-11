"""
Form classes for django-help-pages app
"""

from django import forms

class SearchForm(forms.Form):
    """Super-simple search form """

    query = forms.CharField(
        label="",
        max_length=64,
        required=False
    )

