from django.views.generic import CreateView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.shortcuts import redirect


from .forms import UserCreationForm


class UserCreate(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        login(self.request, user)
        return redirect(self.success_url)
