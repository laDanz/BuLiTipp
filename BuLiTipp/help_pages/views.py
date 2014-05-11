#views for help app
import urllib

from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger
)

from help_pages.models import (
    HelpCategory,
    HelpItem
)

HELP_ITEMS_PER_PAGE = 10

def category_list(request, template_name='help_category_list.html'):

    top_categories = HelpCategory.objects.filter(parent=None).order_by('order')
    branches = []

    for top_category in top_categories:
        subcategories = top_category.subcategories
        if len(subcategories) == 0:
            branches.append([top_category])
        else:
            branches.append([top_category, subcategories])

    help_items = HelpItem.published_objects.all()

    paginator = Paginator(help_items, HELP_ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        helps = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        helps = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        helps = paginator.page(paginator.num_pages)

    return render(request, template_name, {
            'branches': branches,
            'help_items': helps
        }
    )


def item_list(request, identifier=None, template_name="help_item_list.html"):
    """
    Lists all the items in that category
    """
    top_categories = HelpCategory.objects.filter(parent=None).order_by('order')
    branches = []

    for top_category in top_categories:
        subcategories = top_category.subcategories
        if len(subcategories) == 0:
            branches.append([top_category])
        else:
            branches.append([top_category, subcategories])

    try:
        category = HelpCategory.published_objects.get(id=identifier)
    except (HelpCategory.DoesNotExist, ValueError):
        # A ValueError would be trying to pass a string as an int
        try:
            category = HelpCategory.published_objects.get(slug=identifier)
        except HelpCategory.DoesNotExist:
            raise Http404

    help_items = HelpItem.published_objects.filter(category=category).order_by('order')

    trail = category.trail

    return render(request, template_name, {
            'category': category,
            'help_items': help_items,
            'trail': trail,
            'branches': branches
        }
    )


def items_by_tag(request, tag, template_name="help_items_by_tag.html"):
    """
    Lists all the items that are tagged with the relevant category
    """
    #convert tag back to unurlencoded
    relevant_tag = urllib.unquote(tag)

    tagged_items = HelpItem.objects.filter(tag=relevant_tag)

    return render(request, template_name, {
            'tagged_items': tagged_items,
            'relevant_tag': relevant_tag
        }
    )


def single_item(
        request,
        cat_identifier,
        item_identifier,
        template_name='help_single_item.html'):
    """
    Individual help item view
    """
    #see if we can make the identifiers into ints, so we know they'll be pks
    try:
        cat_identifier = int(cat_identifier)
    except:
        pass

    #ditto item_identifiers
    try:
        item_identifier = int(item_identifier)
    except:
        pass
    try:
        #if we're talking ints, we can go straight for it
        if isinstance(item_identifier, int):
            help_item = get_object_or_404(HelpItem, id=item_identifier)
        else:
            #else if we're talking slugs so can't rely on unique ones
            qs = HelpItem.published_objects

            #filter the category first
            if isinstance(cat_identifier, int):
                qs = qs.filter(category=cat_identifier)
            else:
                qs = qs.filter(category__slug=cat_identifier)

            #then try to get the item, which has a slug as an identifier
            help_item = qs.get(slug=item_identifier)

    except (HelpItem.DoesNotExist): #ValueError would be trying to pass a string as an int
        raise Http404


    return render(request, template_name, {'item':help_item } )

def search_results(request, template_name="search_results.html"):
    """
    Displays relevant help items based on the search query entered

    Query is sent as a GET, and uses the very simple form help_pages.forms.SearchForm
    """

    query = request.GET.get('query', None)

    hits = HelpItem.search_manager.search(query)

    return render(request, template_name, {
            'query': query,
            'hits': hits
        }
    )


