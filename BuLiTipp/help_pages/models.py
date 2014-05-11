import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager
from taggit.models import Tag

from help_pages.modelutils import unescape


class PublishedObjectsManager(models.Manager):
    """
    Auto-filters-out disabled/unpublished messages
    """
    def get_query_set(self):
        return super(PublishedObjectsManager, self).get_query_set().exclude(published=False)


class HelpBase(models.Model):
    """
    Abstract base model for Help models
    """

    slug = models.SlugField(
        unique=True,
        help_text=_(
            "Automatically generated; editable, but do "
            "so with caution as it changes URLs"
        )
    )
    published = models.BooleanField(
        _("Published?"),
        default=True
    )
    order = models.FloatField(
        default="1.0",
        help_text=_(
            "Lists will run from smaller numbers at top to bigger at "
            "bottom. Decimal points are allowed for fine control"
        )
    )

    #retain original manager, and add enabled-filtering one
    objects   = models.Manager()
    published_objects = PublishedObjectsManager() #custom manager to make life easier

    class Meta:
        abstract = True
        ordering = ['order']


class HelpCategory(HelpBase):
    """
    Main node for a topic area or sub-topic area
    """
    parent = models.ForeignKey(
        'HelpCategory',
        null=True,
        blank=True
    )
    title = models.CharField(
        blank=False,
        max_length=255,
        help_text=_("No HTML in the this label, please")
    )

    class Meta:
        verbose_name = _("Help category")
        verbose_name_plural = _("Help categories")

    def __unicode__(self):
        return u"%s" % (self.title)

    @property
    def subcategories(self):
        """
        Returns a recursively generated list of any subcategories for the category
        """

        children = []
        subcats = list(self.helpcategory_set.all().order_by('order'))

        for s in subcats:
            cats = s.helpcategory_set.all().order_by('order')
            if len(cats) > 0:
                children.append([s, s.subcategories])
            else:
                children.append([s])
        return children

    @property
    def trail(self):
        trail = []
        parent = self.parent
        trail.append(self)
        while parent is not None:
            trail.append(parent)
            parent = parent.parent

        return trail[::-1]


class HelpItemSearchManager(PublishedObjectsManager):
    """
    Quick manager class to assist with search - extends PublishedObjectsManager
    so that it only searches published objects
    """

    def search(self, search_terms):
        try:
            search_terms = search_terms[:128] #  limit to 128 chars for sanity
            query = None
            qs = self.get_query_set()

            search_terms = unescape(search_terms)
            query = search_terms.lower()
            query = re.sub(r'\W+', ' ', query) #  strip non-alphanumerics from string
            tokens = query.split()

            for t in tokens:
                # Iteratively build a chain of filter()s that narrow down
                # the search selection to contain all words that are or
                # start with every one of the tokens entered
                qs = qs.filter(denormed_search_terms__contains = " %s" % t)

            return qs

        except AttributeError:
            return self.model.objects.none()


class HelpItem(HelpBase):
    """
    Holds the actual help item info
    """
    category = models.ForeignKey('HelpCategory')
    heading = models.CharField(
        blank=False,
        max_length=255,
        help_text=_("No HTML in the this label, please")
    )
    body = models.TextField(
        blank=False,
        help_text=_("Main content for the Help item")
    )

    # Add another manager, to help with search, plus a denormed search
    # content column to speed things up
    search_manager = HelpItemSearchManager()
    denormed_search_terms = models.TextField(
        editable=False,
        blank=True,
        null=True
    )

    tags = TaggableManager(
        verbose_name=_("Tags"),
        blank=True,
        help_text=_(
            "Optional tags that will help this item be shown on other pages. "
            "Put spaces between tags. Avoid all punctuation. If a tag is multiple words, "
            "enclose it in quote marks."
        )
    )

    class Meta:
        verbose_name = _("Help item")
        verbose_name_plural = _("Help item")

    def _get_tags(self):
        return self.tags.all()

    def _set_tags(self, tag_list):
        self.tags.add(tag_list)


    def save(self):
        """
        Overriding save() to denorm the search content - we could
        use Full Text Search instead, but that's not DB-independent.

        Includes category.title to improve hit usefulness
        """
        self.denormed_search_terms = "%s %s %s" % (
            self.heading.lower(),
            self.body.lower(),
            self.category.title.lower()
        )
        super(HelpItem, self).save()

    def __unicode__(self):
         return u"%s: '%s' " % (self.category.title, self.heading)

    @property
    def related_items(self):
        """
        Returns a list of items in the same category as this one
        """
        related = HelpItem.objects.filter(
            tags__name__in=[self.tags.all()]
        ).exclude(
            id=self.id
        )
        return related

