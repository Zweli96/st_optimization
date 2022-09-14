from django import forms
from django.forms import ModelForm
from .models import District, Facility, Health_Worker, Courier, FacilityGroup
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User


class DistrictForm(ModelForm):
    class Meta:
        model = District
        fields = ['name', 'region',
                  'commcare_district_group_id', 'optimization_district']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
            }),
            'region': forms.Select(attrs={
                'class': 'form-control',
            }),
            'commcare_district_group_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CommCare ID',
            }),
            'optimization_district': forms.CheckboxInput(attrs={
                'class': '',
            }),
        }


class FacilityForm(ModelForm):
    class Meta:
        model = Facility
        fields = ['name', 'commcare_name', 'district',
                  'facility_code', 'operator', 'facility_type']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
            }),
            'commcare_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'commcare_name',
            }),
            'district': forms.Select(attrs={
                'class': 'form-control',
            }),
            'facility_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'facility_code',
            }),
            'operator': forms.Select(attrs={
                'class': 'form-control',
            }),
            'facility_type': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class CourierForm(ModelForm):
    class Meta:
        model = Courier
        fields = ['name', 'phone_number', 'district',
                  'commcare_user_name', 'commcare_user_id']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phonenumber starting +265 no space',
            }),
            'district': forms.Select(attrs={
                'class': 'form-control',
            }),
            'commcare_user_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CommCare Username',
            }),
            'commcare_user_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CommCare UserID',
            }),
        }


class Health_WorkerForm(ModelForm):
    class Meta:
        model = Health_Worker
        fields = ['name', 'position', 'phone_number', 'facility']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Position',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phonenumber starting +265 no space',
            }),
            'facility': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


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
        }


class EditUserForm(UserChangeForm):
    model = User
    fields = ['first_name', 'last_name',
              'username', 'email']

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
        }


class FacilityGroupForm(ModelForm):
    class Meta:
        model = FacilityGroup
        fields = ['name', 'code', 'district']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code',
            }),
            'district': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class PasswordResetCustomForm(PasswordResetForm):
    new_password1 = forms.CharField(required=True, label='Password',
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control'}),
                                    error_messages={
                                        'required': 'The password cannot be empty'})
    new_password2 = forms.CharField(required=True, label='Password (Repeat)',
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control'}),
                                    error_messages={
                                        'required': 'The password cannot be empty'})
