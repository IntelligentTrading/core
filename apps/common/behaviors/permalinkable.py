from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse


class Permalinkable(models.Model):

    slug = models.SlugField(null=True, blank=True, max_length=255)

    class Meta:
        abstract = True

    def get_url_kwargs(self, **kwargs):
        kwargs.update(getattr(self, 'url_kwargs', {}))
        return kwargs

    @models.permalink
    def get_absolute_url(self):
        url_kwargs = self.get_url_kwargs(slug=self.slug)
        return reverse(self.url_name, (), url_kwargs)


# just an example, because signals are not part of the abstract model
@receiver(pre_save, sender=Permalinkable)
def pre_save(self, instance, *args, **kwargs):
    from django.utils.text import slugify
    if not instance.slug:
        instance.slug = slugify(self.slug_source)
