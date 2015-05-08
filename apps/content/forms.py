from django import forms
from content.models import Page, Tag

class PageForm(forms.ModelForm):
    title = forms.CharField()

    class Meta:
        model = Page
        fields = ('title','body')
