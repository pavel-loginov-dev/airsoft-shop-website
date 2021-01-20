import operator
from functools import reduce

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType

from .models import (
    Category,
    LatestItemManager,
    AmmoItem,
    GunItem,
    AccessoryItem,
    GearItem,
    Customer,
    Cart,
    CartItem
)


CATEGORY_MODEL = {
    GunItem.category_parent: GunItem,
    AmmoItem.category_parent: AmmoItem,
    AccessoryItem.category_parent: AccessoryItem,
    GearItem.category_parent: GearItem,
}


def index(request):
    """Renders the home page of the site."""
    items = LatestItemManager.get_last_items()
    return TemplateResponse(request, 'index.html', {'items': items})


def item_details(request, category_slug, item_slug):
    """Renders an item details page."""
    root_category = Category.objects.get(slug=category_slug).get_root().name
    model = CATEGORY_MODEL[root_category]
    item = get_object_or_404(model, slug=item_slug)
    return TemplateResponse(request, 'item_details.html', {'item': item})


# TODO: Read `mptt` docs and find out a better way to filter items.
def items_category(request, category_slug):
    """Renders a page with items by category."""
    category = Category.objects.get(slug=category_slug)
    root_category = category.get_root()
    model = CATEGORY_MODEL[root_category.name]
    categories = list(category.get_children())
    categories.append(category)
    conditions = reduce(operator.or_, [Q(**{"category": category})
                                       for category in categories])
    items = model.objects.filter(conditions)
    context = {'category': category, 'items': items}
    return TemplateResponse(request, 'category.html', context)


def customer_cart(request):
    """Renders a page with customer's cart."""
    return TemplateResponse(request, 'customer_cart.html', {})


def add_to_cart(request, category_slug, item_slug):
    """Adds a `CartItem` to customer's cart."""
    root_category = Category.objects.get(slug=category_slug).get_root().name
    item = get_object_or_404(CATEGORY_MODEL[root_category], slug=item_slug)
    ct = ContentType.objects.get_for_model(item)
    cart = request.initial_data['cart']
    cart_item, created = CartItem.objects.get_or_create(
        customer=cart.owner, cart=cart, content_type=ct, object_id=item.id,
        total_price=item.price
    )
    cart.items.add(cart_item)
    return HttpResponseRedirect(reverse_lazy('customer_cart'))
