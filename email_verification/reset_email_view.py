from django.shortcuts import render
from .reset_email_form import ResetEmailForm
from .confirm import verify_token
from member.models import Member

def complete_test(request):
    form = ResetEmailForm({
            'success': False,
            'member_id': 0,
            'member_email': None,
            'new_email': None
        })
    return render(request, '../templates/email_reset_complete.html', {'form': form})

def reset_email(request, token):
    if request.method == 'POST':
        form = ResetEmailForm(request.POST)
        if form.is_valid():
            # Save new_password
            new_email = form.cleaned_data['new_email']
            member_id = form.cleaned_data['member_id']
            member = Member.objects.filter(id=member_id).first()
            member.email = new_email
            member.save()
            return render(request, '../templates/email_reset_complete.html', {'form': form})

        return render(
            request,
            'email_reset_confirm.html',
            {
                'form': form,
                'success': form.cleaned_data['success'],
                'member_id': form.cleaned_data['member_id'],
                'member_email': new_email,
                'request': request
            }
        )
    
    success, member = verify_token(token)
    member_id = member.id if member else 0
    new_email = member.new_email if member else None
    member_email = member.email if member else None
    #success=True
    #member_id="94591"
    #member_email="ha@comicul-inc.com"
    form = ResetEmailForm({
            'success': success,
            'member_id': member_id,
            'member_email': member_email,
            'new_email': new_email
        })
    return render(
        request,
        '../templates/email_reset_confirm.html',
        {
            'form': form,
            'token': token,
            'success': success,
            'member_id': member_id,
            'new_mail': new_email,
            'member_email': member_email,
            'request': request
        }
    )
