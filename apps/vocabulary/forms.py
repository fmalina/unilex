from django import forms
from vocabulary.models import Concept, Vocabulary


class ConceptForm(forms.ModelForm):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ConceptForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

    class Meta:
        model = Concept
        exclude = ('related', 'vocabulary', 'parent')


class NewChildConceptForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Concept
        fields = ('name',)


class VocabularyForm(forms.ModelForm):
    title = forms.CharField()

    class Meta:
        model = Vocabulary
        fields = ('title', 'node_id', 'description', 'language',
                  'private', 'source')


class UploadFileForm(forms.Form):
    file = forms.FileField()


TO_CONCEPT = forms.ModelChoiceField(
    queryset=Concept.objects.all(),
    widget=forms.TextInput(attrs={'class': 'autocomplete',
                                  'placeholder': 'Type concept and choose'})
)


class RelatedForm(forms.ModelForm):
    to_concept = TO_CONCEPT

    class Meta:
        model = Concept.related.through
        exclude = ('from',)


class ParentForm(forms.ModelForm):
    to_concept = TO_CONCEPT

    class Meta:
        model = Concept.parent.through
        exclude = ('from',)
