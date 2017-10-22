from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class archive(models.Model):

    url = models.CharField(
        max_length=50,
        null=True,
        verbose_name=_('url')

    )
    content = models.TextField(
        max_length=100000,
        null=True,
        verbose_name=_('content')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('archive')
        verbose_name_plural = _('archives')


    def __str__(self):
        return str(self.url)
