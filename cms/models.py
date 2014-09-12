from django.utils import timezone

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cms import utils
from cms.git.models import GitPage, GitCategory


class Category(models.Model):
    """
    Category model to be used for categorization of content. Categories are
    high level constructs to be used for grouping and organizing content,
    thus creating a site's table of contents.
    """
    uuid = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        editable=False)
    title = models.CharField(
        max_length=200,
        help_text='Short descriptive name for this category.',
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text='Some titles may be the same and cause confusion in admin '
                  'UI. A subtitle makes a distinction.',
    )
    slug = models.SlugField(
        max_length=255,
        db_index=True,
        unique=True,
        help_text='Short descriptive unique name for use in urls.',
    )

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Post(models.Model):

    class Meta:
        ordering = ('-created_at',)

    uuid = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        editable=False)
    title = models.CharField(
        _("Title"),
        max_length=200, help_text=_('A short descriptive title.'),
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_(
            'Some titles may be the same and cause confusion in admin'
            'UI. A subtitle makes a distinction.'),
    )
    slug = models.SlugField(
        editable=False,
        max_length=255,
        db_index=True,
        unique=True,
    )
    description = models.TextField(
        help_text=_(
            'A short description. More verbose than the title but'
            'limited to one or two sentences.'),
        blank=True,
        null=True,
    )
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(
        _('Created Date & Time'),
        blank=True,
        db_index=True,
        help_text=_(
            'Date and time on which this item was created. This is'
            'automatically set on creation, but can be changed subsequently.')
    )
    modified_at = models.DateTimeField(
        _('Modified Date & Time'),
        db_index=True,
        editable=False,
        auto_now=True,
        help_text=_(
            'Date and time on which this item was last modified. This'
            'is automatically set each time the item is saved.')
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        null=True,
        help_text=_('Categorizing this item.')
    )
    primary_category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        help_text=_(
            "Primary category for this item. Used to determine the"
            "object's absolute/default URL."),
        related_name="primary_modelbase_set",
    )

    def save(self, *args, **kwargs):
        # set title as slug uniquely
        self.slug = utils.generate_slug(self)

        # set created time to now if not already set.
        if not self.created_at:
            self.created_at = timezone.now()

        super(Post, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.subtitle:
            return '%s - %s' % (self.title, self.subtitle)
        else:
            return self.title


@receiver(post_save, sender=Post)
def auto_save_post_to_git(sender, instance, created, **kwargs):
    def update_fields(page, post):
        page.title = instance.title
        page.subtitle = instance.subtitle
        page.slug = instance.slug
        page.description = instance.description
        page.content = instance.content
        page.created_at = instance.created_at
        page.modified_at = instance.modified_at

        if instance.primary_category and instance.uuid:
            category = GitCategory.get(instance.primary_category.uuid)
            page.primary_category = category

    if created:
        page = GitPage()
        update_fields(page, instance)
        page.save(True, message='Page created: %s' % instance.title)

        # store the page's uuid on the Post instance without triggering `save`
        Post.objects.filter(pk=instance.pk).update(uuid=page.uuid)
    else:
        page = GitPage.get(instance.uuid)
        update_fields(page, instance)
        page.save(True, message='Page updated: %s' % instance.title)

    utils.sync_repo()


@receiver(post_delete, sender=Post)
def auto_delete_post_to_git(sender, instance, **kwargs):
    GitPage.delete(
        instance.uuid, True, message='Page deleted: %s' % instance.title)


@receiver(post_save, sender=Category)
def auto_save_category_to_git(sender, instance, created, **kwargs):
    def update_fields(category, post):
        category.title = instance.title
        category.subtitle = instance.subtitle
        category.slug = instance.slug

    if created:
        category = GitCategory()
        update_fields(category, instance)
        category.save(True, message='Category created: %s' % instance.title)

        # store the page's uuid on the Post instance without triggering `save`
        Category.objects.filter(pk=instance.pk).update(uuid=category.uuid)
    else:
        category = GitCategory.get(instance.uuid)
        update_fields(category, instance)
        category.save(True, message='Category updated: %s' % instance.title)

    utils.sync_repo()


@receiver(post_delete, sender=Category)
def auto_delete_category_to_git(sender, instance, **kwargs):
    GitCategory.delete(
        instance.uuid, True, message='Category deleted: %s' % instance.title)
