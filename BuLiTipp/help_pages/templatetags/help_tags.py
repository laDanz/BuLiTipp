from django import template
register = template.Library()

from help_pages.forms import SearchForm
from help_pages.models import HelpItem


@register.inclusion_tag('includes/help_search_form.html')
def help_search_form(query=None):

    """
    Quick inclusion tag to spit out a search input for the help
    section.

    It takes an optional 'query' argument, which enables you to
    pass in the just-requested search query so that the form
    has it pre-set if you wish. For example, if your template's
    context includes the most recent search query as the
    variable 'query', just use this in your template:

    {% help_search_form query %}

    to ensure the search box contains the terms that were just
    searched for. This is optional, of course, and solely

    {% help_search_form %}

    will render the (empty) form too.

    Feel free to ignore this entire tag if you prefer - it's
    just a nicety.

    """

    kwargs = {}

    if query:
        kwargs['query'] = query

    search_form = SearchForm(kwargs)

    return  {
        'search_form':search_form,
    }


@register.inclusion_tag('includes/links_to_items_for_tag.html')
def links_to_items_for_tag(tag, limit=10):

    """
    Inclusion tag to render `limit` links to help items with the tag passed in as a UL

    Takes one required and one optional arguments: `tag` and `limit`
    """

    if limit < 0:  # Watch for silly buggers
        limit = 10

    items = HelpItem.objects.filter(tags=tag).distinct()

    return {
        'items': items
    }
