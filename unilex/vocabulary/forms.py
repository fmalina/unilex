from django import forms
from unilex.vocabulary.models import Concept, Vocabulary


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
    permit = forms.BooleanField(
        required=False,
        label='Permit storage of your raw file for inspection and troubleshooting'
    )


TO_CONCEPT = forms.ModelChoiceField(
    queryset=Concept.objects.all(),
    widget=forms.TextInput(attrs={'class': 'autocomplete',
                                  'placeholder': 'Type concept and choose'})
)


class RelatedForm(forms.ModelForm):
    predicate = TO_CONCEPT

    class Meta:
        model = Concept.related.through
        exclude = ('subject',)


class ParentForm(forms.ModelForm):
    to_concept = TO_CONCEPT

    class Meta:
        model = Concept.parent.through
        exclude = ('from',)


class AutoBotHoneypotSignupForm(forms.Form):
    def signup(self, request, user):
        """Stop bot signups using a honeypot method"""
        if request.POST.get('bname'):
            raise Exception('Bot trying to signup')
