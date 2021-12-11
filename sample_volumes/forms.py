from django import forms
from django.forms import ModelForm
from .models import District, Facility, Health_Worker
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DistrictForm(ModelForm):
    class Meta:
        model = District
        fields = '__all__'


class FacilityForm(ModelForm):
    class Meta:
        model = Facility
        fields = '__all__'


class Health_WorkerForm(ModelForm):
    class Meta:
        model = Health_Worker
        fields = '__all__'


class CreateUserForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'type': 'password', 'align': 'center', 'placeholder': 'password'}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'type': 'password', 'align': 'center', 'placeholder': 'password'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'}),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email'}),
            # 'password1': forms.PasswordInput(attrs={
            #     'class': 'form-control',
            #     'type': 'password',
            #     'name': 'password',
            #     'placeholder': 'Password'}),
            # 'password2': forms.PasswordInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Confirm'})
        }
