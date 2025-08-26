from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from . import models

CustomUser = get_user_model()

attrs = {'class': 'form-control'}

class LoginForm(forms.Form):
    username = forms.CharField(label='نام کاربری', widget=forms.TextInput(attrs=attrs))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(attrs=attrs))

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='نام کاربری', max_length=100, widget=forms.TextInput(attrs=attrs))
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(attrs=attrs))
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput(attrs=attrs))
    first_name = forms.CharField(label='نام', max_length=100, widget=forms.TextInput(attrs=attrs))
    last_name = forms.CharField(label='نام خانوادگی', max_length=100, widget=forms.TextInput(attrs=attrs))

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'user_type', 'first_name', 'last_name']

        widgets = {
            'user_type': forms.Select(attrs=attrs),
        }

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.CustomUser
        fields = ['username', 'user_type', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class SelectManagerForm(forms.ModelForm):
    class Meta:
        model = models.CustomUser
        fields = ['manager']

        widgets = {
            'manager': forms.Select(attrs=attrs),
        }

class ProfileEmployeeForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        exclude = ('user', 'status')

    def __init__(self, *args, **kwargs):
        super(ProfileEmployeeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

            if self.fields[field].label in ['تاریخ تولد']:
                self.fields[field].widget.attrs.update({
                    'data-jdp': '',
                    'autocomplete': 'off'
                })

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        exclude = ('user', )

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class SuperAdminBulkActivityForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=models.CustomUser.objects.all(),
        widget=forms.SelectMultiple(attrs=attrs),
        label='کاربران'
    )
    title = forms.CharField(max_length=1000, label='عنوان', widget=forms.TextInput(attrs=attrs))
    body = forms.CharField(label='توضیحات', widget=forms.Textarea(attrs=attrs))
    start_date = forms.CharField(label='تاریخ شروع', widget=forms.TextInput(attrs={**attrs, 'data-jdp': '', 'autocomplete': 'off'}))
    start_time = forms.TimeField(label='ساعت شروع', widget=forms.TimeInput(attrs={**attrs, 'type': 'time'}))
    end_date = forms.CharField(label='تاریخ پایان', widget=forms.TextInput(attrs={**attrs, 'data-jdp': '', 'autocomplete': 'off'}))
    end_time = forms.TimeField(label='ساعت پایان', widget=forms.TimeInput(attrs={**attrs, 'type': 'time'}))
    sensitivity = forms.ChoiceField(choices=models.Activity.SENSITIVITY_CHOICES, label='حساسیت', widget=forms.Select(attrs=attrs))

class ManagerBulkActivityForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=models.CustomUser.objects.none(),
        widget=forms.SelectMultiple(attrs=attrs),
        label='کارمندان'
    )
    title = forms.CharField(max_length=1000, label='عنوان', widget=forms.TextInput(attrs=attrs))
    body = forms.CharField(label='توضیحات', widget=forms.Textarea(attrs=attrs))
    start_date = forms.CharField(label='تاریخ شروع', widget=forms.TextInput(attrs={**attrs, 'data-jdp': '', 'autocomplete': 'off'}))
    start_time = forms.TimeField(label='ساعت شروع', widget=forms.TimeInput(attrs={**attrs, 'type': 'time'}))
    end_date = forms.CharField(label='تاریخ پایان', widget=forms.TextInput(attrs={**attrs, 'data-jdp': '', 'autocomplete': 'off'}))
    end_time = forms.TimeField(label='ساعت پایان', widget=forms.TimeInput(attrs={**attrs, 'type': 'time'}))
    sensitivity = forms.ChoiceField(choices=models.Activity.SENSITIVITY_CHOICES, label='حساسیت', widget=forms.Select(attrs=attrs))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['users'].queryset = CustomUser.objects.filter(
                manager=user,
                user_type='3',
                user_profile__status='2'
            )

class ActivityUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Activity
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ActivityUpdateForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if self.fields[field].label in ['وضعیت انجام', 'وضعیت نمایش']:
                pass
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
            
            if self.fields[field].label in ['تاریخ شروع', 'تاریخ پایان']:
                self.fields[field].widget.attrs.update({
                    'data-jdp': '',
                    'autocomplete': 'off'
                })
            
            if self.fields[field].label in ['ساعت شروع', 'ساعت پایان']:
                self.fields[field].widget.attrs.update({
                    'type': 'time'
                })