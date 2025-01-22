from django import forms
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect


class UpdateProfile(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UpdateProfile(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('profile'))
    else:
        form = UpdateProfile(instance=request.user)

    return render(request, 'profile.html', {'form': form})
