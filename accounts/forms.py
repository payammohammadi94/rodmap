from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length = 50,label="نام کاربری")
    password = forms.CharField(max_length = 50,label="رمز عبور")