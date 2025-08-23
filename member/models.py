from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from s3direct.fields import S3DirectField
# Create your models here.
class Member(models.Model):
    ADMIN = 'ADMIN'
    USER = 'USER'
    MEMBER_TYPE = (
        (ADMIN, ADMIN),
        (USER, USER),
    )
    image = S3DirectField(dest='member_images', blank=True)
    email = models.CharField(max_length=60, blank=False)
    type = models.CharField(choices=MEMBER_TYPE, max_length=15, blank=False)
    first_name = models.CharField(max_length=128, blank=False)
    last_name = models.CharField(max_length=128, blank=False)
    telnumber = models.CharField(max_length=40, blank=True, null=True)
    password = models.CharField(max_length=128, blank=False, validators=[MinLengthValidator(6)])
    active_notification = models.BooleanField(blank=False, default=True)
    udid = models.CharField(max_length=64, blank=True, null=True)
    login_date = models.DateTimeField(blank=True, null=True)
    is_valid_email = models.BooleanField(blank=True, default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    expo_push_token = models.CharField(max_length=255, blank=True, null=True)
    

    class Meta:
        managed = True
        db_table = 'member'
        ordering = ('-id',)
        unique_together = ('email', 'type',)

    def __str__(self):
        res = str(self.id)
        if self.first_name:
            res = res + ': ' + self.first_name
        if self.last_name:
            res = res + ' ' + self.last_name
        if self.type:
            res = res + ' (' + self.type + ')'
        return res

    def image_tag(self):
        res = None
        if self.image:
            res = mark_safe('<img src="{src}" width="{width}" />'
            .format(
                src=self.image if self.image else '',
                width=80,
                height='auto'
            ))
        return res

    def full_name(self):
        res = ''
        if self.first_name:
            res = res + self.first_name
        if self.last_name:
            res = res + ' ' + self.last_name
        return res

    def set_is_valid_email(self, is_valid):
        self.is_valid_email = is_valid
        self.save()
