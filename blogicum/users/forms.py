from django import forms
from django.contrib.auth import get_user_model


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'password',
            'username',
            'first_name',
            'last_name',
            'email',
        )
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('E-mail такой существует')
        return email
