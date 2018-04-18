from django import forms
from tag.models import Record
from vocabulary.forms import TO_CONCEPT


class TagForm(forms.Form):
    to_concept = TO_CONCEPT


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['title']
        readonly_fields = ['url']
