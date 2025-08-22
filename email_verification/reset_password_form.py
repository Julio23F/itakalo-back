from django import forms
from django.shortcuts import render

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    member_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    member_email = forms.CharField(widget=forms.HiddenInput(), required=False)
    success = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self,*args,**kwargs):
        member_id = args[0]['member_id']
        member_email = args[0]['member_email']
        success = args[0]['success']
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['member_id'].widget = forms.HiddenInput(attrs={'member_id': member_id})
        self.fields['member_email'].widget = forms.HiddenInput(attrs={'member_email': member_email})
        self.fields['success'].widget = forms.HiddenInput(attrs={'success': success})

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        member_id = cleaned_data.get('member_id')
        member_email = cleaned_data.get('member_email')
        success = cleaned_data.get('success')
        if (not new_password) or (new_password != confirm_password):
            raise forms.ValidationError('Password and Confirm Password must be the same.')

