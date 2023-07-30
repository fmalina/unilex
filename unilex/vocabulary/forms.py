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
    file = forms.FileField(required=False)
    permit = forms.BooleanField(
        required=False,
        label='Store raw file for inspection'
    )
    content = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 60}),
        label='Or paste content here'
    )


def link_concept(qs=Concept.objects.all()):
    return forms.ModelChoiceField(
        queryset=qs,
        widget=forms.TextInput(attrs={
            'class': 'autocomplete',
            'placeholder': 'Type concept and choose'
        })
    )


class RelatedForm(forms.ModelForm):
    object = link_concept()

    class Meta:
        model = Concept.related.through
        exclude = ('subject',)


class ParentForm(forms.ModelForm):
    to_concept = link_concept()

    class Meta:
        model = Concept.parent.through
        exclude = ('from',)


class AutoBotHoneypotSignupForm(forms.Form):
    def signup(self, request, user):
        """Stop bot signups using a honeypot method"""
        honeypot = request.POST.get('bname')
        if honeypot:
            user.delete()
            raise Exception(f'Bot trying to signup')
