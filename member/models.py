from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

class Preference(models.Model):
    T_SHIRT = 'T_SHIRT'
    PANTALON = 'PANTALON'
    ROBE = 'ROBE'
    CHAUSSURE = 'CHAUSSURE'
    VESTE = 'VESTE'
    ELECTRONIQUE = 'ELECTRONIQUE'
    ACCESSOIRES = 'ACCESSOIRES'

    PREFERENCE_CHOICES = [
        (T_SHIRT, _('T-shirt')),
        (PANTALON, _('Pantalon')),
        (ROBE, _('Robe')),
        (CHAUSSURE, _('Chaussure')),
        (VESTE, _('Veste')),
        (ELECTRONIQUE, _('Électronique')),
        (ACCESSOIRES, _('Accessoires')),
    ]

    name = models.CharField(max_length=50, choices=PREFERENCE_CHOICES, unique=True)

    class Meta:
        db_table = 'preference'
        ordering = ['name']

    def __str__(self):
        return self.name


class Member(models.Model):
    ADMIN = 'ADMIN'
    USER = 'USER'
    MEMBER_TYPE = (
        (ADMIN, ADMIN),
        (USER, USER),
    )

    image = models.TextField(blank=True, null=True)
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

    # Champs pour Google OAuth
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_picture = models.URLField(null=True, blank=True)
    is_google_user = models.BooleanField(default=False)

    # Relation ManyToMany pour les préférences
    preferences = models.ManyToManyField(Preference, related_name='members', blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
        if self.image:
            return mark_safe(f'<img src="{self.image}" width="80" height="auto" />')
        return None

    def full_name(self):
        res = ''
        if self.first_name:
            res += self.first_name
        if self.last_name:
            res += ' ' + self.last_name
        return res

    def set_is_valid_email(self, is_valid):
        self.is_valid_email = is_valid
        self.save()
