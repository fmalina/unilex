from django import forms
from django.contrib.auth import get_user_model
from unilex.vocabulary.models import Concept, Vocabulary, Authority

User = get_user_model()


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


class BaseRelatedFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, predicates=None, **kwargs):
        self.predicates = predicates
        super(BaseRelatedFormSet, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super(BaseRelatedFormSet, self).get_form_kwargs(index)
        kwargs['predicates'] = self.predicates
        return kwargs


class RelatedForm(forms.ModelForm):
    predicate = forms.ChoiceField(choices=[])
    object = link_concept()

    class Meta:
        model = Concept.related.through
        exclude = ('subject',)

    def __init__(self, *args, predicates=None, **kwargs):
        super(RelatedForm, self).__init__(*args, **kwargs)
        self.fields['predicate'].choices = predicates or []

    def clean_predicate(self):
        pk = self.cleaned_data['predicate']
        if pk:
            try:
                return Concept.objects.get(pk=pk)
            except Concept.DoesNotExist:
                pass
        raise forms.ValidationError("Invalid predicate selected.")


class AuthorityForm(forms.ModelForm):
    email_to_add = forms.EmailField(
        required=False,
        label="Add user by email"
    )

    class Meta:
        model = Authority
        fields = ['name', 'website']

    def clean_email_to_add(self):
        email = self.cleaned_data.get("email_to_add")
        if email:
            try:
                _user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("No user found with this email.")
        return email

    def save(self, commit=True):
        email = self.cleaned_data.get("email_to_add")
        if email:
            user = User.objects.get(email=email)
            if user:
                self.instance.users.add(user)
        return super().save(commit=commit)


class PredicatesForm(forms.ModelForm):
    concept = link_concept()

    class Meta:
        model = Vocabulary.predicates.through
        exclude = ('vocabulary',)


class AutoBotHoneypotSignupForm(forms.Form):
    def signup(self, request, user):
        """Stop bot signups using a honeypot method"""
        honeypot = request.POST.get('bname')
        if honeypot:
            user.delete()
            raise Exception(f'Bot trying to signup')
