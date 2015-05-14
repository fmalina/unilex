import settings
from django.forms import Form, ModelForm, CharField, ChoiceField, ModelChoiceField, FileField
from django.forms.widgets import TextInput, Textarea, HiddenInput
from django.forms.formsets import formset_factory
from vocabulary.models import Concept, Vocabulary

class ConceptForm(ModelForm):
    name = CharField()

    def __init__(self, *args, **kwargs):
        super(ConceptForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

    class Meta:
        model = Concept
        exclude = ('node_id', 'related', 'vocabulary', 'parent')

class NewChildConceptForm(ModelForm):
    name = CharField()

    class Meta:
        model = Concept
        fields = ('name',)

class VocabularyForm(ModelForm):
    title = CharField()

    class Meta:
        model = Vocabulary
        fields = 'title', 'node_id', 'description', 'private' #, 'queries'

class UploadFileForm(Form):
    file = FileField()

TO_CONCEPT = ModelChoiceField(queryset=Concept.objects.all(), widget=TextInput(attrs={'class':'autocomplete'}))

class RelatedForm(ModelForm):
    to_concept = TO_CONCEPT
    class Meta:
        model = Concept.related.through
        exclude = ('from',)

class ParentForm(ModelForm):
    to_concept = TO_CONCEPT
    class Meta:
        model = Concept.parent.through
        exclude = ('from',)
