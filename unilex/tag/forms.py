from django import forms
from unilex.tag.models import Record
from unilex.vocabulary.forms import link_concept


class TagForm(forms.Form):
    object = link_concept()


class RecordForm(forms.ModelForm):
    desc = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label='Description'
    )

    class Meta:
        model = Record
        fields = ['title', 'desc', 'key']
