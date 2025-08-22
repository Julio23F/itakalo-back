from django.shortcuts import render
from .change_password_form import ChangePasswordForm
from .confirm import verify_token
from member.models import Member

def change_password(request, token):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            # Save new_password
            new_password = form.cleaned_data['new_password']
            member_id = form.cleaned_data['member_id']
            member = Member.objects.filter(id=member_id).first()
            member.password = new_password
            member.save()
            return render(request, '../templates/password_change_complete.html', {'form': form})

        return render(
            request,
            'email_reset_confirm.html',
            {
                'form': form,
                'success': form.cleaned_data['success'],
                'member_id': form.cleaned_data['member_id'],
                'member_email': email,
                'request': request
            }
        )
    
    success, member = verify_token(token)
    member_id = member.id if member else 0
    new_password = member.new_password if member else None
    member_email = member.email if member else None
    #success=True
    #member_id="94591"
    #member_email="ha@comicul-inc.com"
    form = ChangePasswordForm({
            'success': success,
            'member_id': member_id,
            'member_email': member_email,
            'new_password': new_password
        })
    return render(
        request,
        '../templates/password_change_confirm.html',
        {
            'form': form,
            'token': token,
            'success': success,
            'member_id': member_id,
            'new_password': new_password,
            'member_email': member_email,
            'request': request
        }
    )
