# models.py
from django.db import models
from django.utils.safestring import mark_safe
from member.models import Member

class Product(models.Model):
    DONATION = 'DONATION'
    SALE = 'SALE'
    PRODUCT_TYPE = (
        (DONATION, DONATION),
        (SALE, SALE),
    )

    title = models.CharField(max_length=128, blank=False)
    image = models.URLField(blank=True, null=True)
    type = models.CharField(choices=PRODUCT_TYPE, max_length=15, blank=False)
    description = models.CharField(max_length=128, blank=False)

    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='products')

    likes = models.ManyToManyField(Member, related_name='liked_products', blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product'
        ordering = ('-id',)

    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image}" width="80" height="auto" />')
        return None

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
