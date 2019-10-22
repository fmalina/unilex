from django import forms
from tag.models import Record
from vocabulary.forms import TO_CONCEPT


class TagForm(forms.Form):
    predicate = TO_CONCEPT


class RecordForm(forms.ModelForm):
    desc = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label="Description")

    class Meta:
        model = Record
        fields = ['title', 'desc', 'key']
