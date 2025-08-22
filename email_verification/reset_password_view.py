from django.shortcuts import render
from .reset_password_form import ResetPasswordForm
from .confirm import verify_token
from member.models import Member

def reset_password(request, token):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Save new_password
            new_password = form.cleaned_data['new_password']
            member_id = form.cleaned_data['member_id']
            member = Member.objects.filter(id=member_id).first()
            member.password = new_password
            member.save()
            return render(request, 'password_reset_complete.html', {'form': form})

        return render(
            request,
            'password_reset_confirm.html',
            {
                'form': form,
                'success': form.cleaned_data['success'],
                'member_id': form.cleaned_data['member_id'],
                'member_email': form.cleaned_data['member_email'],
                'request': request
            }
        )
    
    success, member = verify_token(token)
    member_id = member.id if member else 0
    member_email = member.email if member else None
    form = ResetPasswordForm({
            'success': success,
            'member_id': member_id,
            'member_email': member_email
        })
    return render(
        request,
        'password_reset_confirm.html',
        {
            'form': form,
            'token': token,
            'success': success,
            'member_id': member_id,
            'member_email': member_email,
            'request': request
        }
    )
