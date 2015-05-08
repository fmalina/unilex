from django.forms import Form, CharField, IntegerField, ModelChoiceField
from django.forms.widgets import TextInput, Textarea, HiddenInput
from vocabulary.models import Concept

class TagForm(Form):
    to_concept = ModelChoiceField(queryset=Concept.objects.all(), widget=TextInput(attrs={'class':'autocomplete'}))

class RecordForm(Form):
    title = CharField(required=False)
    description = CharField(widget=Textarea(attrs={'cols':'100','rows':'3'}), required=False)
    notes = CharField(widget=Textarea(attrs={'cols':'100','rows':'3'}), required=False)
    name = CharField(widget=TextInput(attrs={'disabled':'disabled'}), required=False)
    node_id = IntegerField(widget=HiddenInput())
    auth_token = CharField(max_length=32, widget=HiddenInput(), required=False)