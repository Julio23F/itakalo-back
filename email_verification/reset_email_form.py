from django import forms
from django.shortcuts import render

class ResetEmailForm(forms.Form):
    member_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    member_email = forms.CharField(widget=forms.HiddenInput(), required=False)
    new_email = forms.CharField(widget=forms.HiddenInput(), required=False)
    success = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self,*args,**kwargs):
        member_id = args[0]['member_id']
        member_email = args[0]['member_email']
        new_email = args[0]['new_email']
        success = args[0]['success']
        super(ResetEmailForm, self).__init__(*args, **kwargs)
        self.fields['member_id'].widget = forms.HiddenInput(attrs={'member_id': member_id})
        self.fields['member_email'].widget = forms.HiddenInput(attrs={'member_email': member_email})
        self.fields['member_email'].widget = forms.HiddenInput(attrs={'new_email': new_email})
        self.fields['success'].widget = forms.HiddenInput(attrs={'success': success})

    def clean(self):
        cleaned_data = super(ResetEmailForm, self).clean()
        member_id = cleaned_data.get('member_id')
        member_email = cleaned_data.get('member_email')
        new_email = cleaned_data.get('new_email')
        success = cleaned_data.get('success')

