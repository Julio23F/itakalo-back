from django.db import models
from django.utils.safestring import mark_safe
from s3direct.fields import S3DirectField

# On suppose que tu as un modèle Member
from member.models import Member  

class Product(models.Model):
    DONATION = 'DONATION'
    SALE = 'SALE'
    PRODUCT_TYPE = (
        (DONATION, DONATION),
        (SALE, SALE),
    )

    title = models.CharField(max_length=128, blank=False)
    image = S3DirectField(dest='product_images', blank=True)
    type = models.CharField(choices=PRODUCT_TYPE, max_length=15, blank=False)
    description = models.CharField(max_length=128, blank=False)

    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='products')

    likes = models.ManyToManyField(Member, related_name='liked_products', blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'product'
        ordering = ('-id',)

    def image_tag(self):
        if self.image:
            return mark_safe(
                '<img src="{src}" width="{width}" height="auto" />'.format(
                    src=self.image,
                    width=80
                )
            )
        return None

    def total_likes(self):
        """Retourne le nombre total de likes"""
        return self.likes.count()

    def __str__(self):
        return self.title
