from django import forms
from django.shortcuts import render

class ChangePasswordForm(forms.Form):
    member_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    member_email = forms.CharField(widget=forms.HiddenInput(), required=False)
    password = forms.CharField(widget=forms.HiddenInput(), required=False)
    new_password = forms.CharField(widget=forms.HiddenInput(), required=False)
    success = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self,*args,**kwargs):
        member_id = args[0]['member_id']
        member_email = args[0]['member_email']
        new_password = args[0]['new_password']
        success = args[0]['success']
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['member_id'].widget = forms.HiddenInput(attrs={'member_id': member_id})
        self.fields['member_email'].widget = forms.HiddenInput(attrs={'member_email': member_email})
        self.fields['password'].widget = forms.HiddenInput(attrs={'new_email': new_password})
        self.fields['new_password'].widget = forms.HiddenInput(attrs={'new_email': new_password})
        self.fields['success'].widget = forms.HiddenInput(attrs={'success': success})

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        member_id = cleaned_data.get('member_id')
        member_email = cleaned_data.get('member_email')
        new_password = cleaned_data.get('new_password')
        success = cleaned_data.get('success')

