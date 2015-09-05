from django import forms
from tag.models import Record, Tag
from vocabulary.models import Concept

class TagForm(forms.Form):
    to_concept = forms.ModelChoiceField(
        queryset=Concept.objects.all(),
        widget=forms.TextInput(attrs={'class':'autocomplete'})
        )
"""
# remote CMS integration

class RecordForm(forms.Form):
    title   = forms.CharField(required=False)
    desc    = forms.CharField(widget=forms.Textarea(attrs={'cols':'100','rows':'3'}), required=False)
    notes   = forms.CharField(widget=forms.Textarea(attrs={'cols':'100','rows':'3'}), required=False)
    name    = forms.CharField(widget=forms.TextInput(attrs={'disabled':'disabled'}), required=False)
    node_id = forms.IntegerField(widget=forms.HiddenInput())
    auth_token = forms.CharField(max_length=32, widget=forms.HiddenInput(), required=False)
"""

class RecordForm(forms.ModelForm):

    class Meta:
        model = Record
        fields = ('title','desc','url')
