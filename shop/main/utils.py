"""Module contains decorators that gets data from database for views."""
from functools import wraps

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from .models import CATEGORY_MODEL, Category, CartItem


def get_item(view):
    """Adds an instance of subclass of Item to request and calls view.

    Gets `category_slug` and `item_slug` from url and gets *Item object
    by slugs and adds `item` and it's ContentType to request information.
    Then sends request to a view.

    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        request = args[0]
        category_slug = kwargs['category_slug']
        item_slug = kwargs['item_slug']
        root_category = get_object_or_404(Category, slug=category_slug)
        model = CATEGORY_MODEL[root_category.get_root().name]
        item = get_object_or_404(model, slug=item_slug)
        ct = ContentType.objects.get_for_model(item)
        request.initial_data['item'] = {'object': item, 'content_type': ct}
        return view(request)
    return wrapper


def get_cart_item(view):
    """Adds an instance of CartItem to request and calls view.

    Gets CartItem or creates new one and adds to request information.
    Then sends request to a view.

    """
    @get_item
    @wraps(view)
    def wrapper(*args):
        request = args[0]
        cart = request.initial_data['cart']
        cart_item, created = CartItem.objects.get_or_create(
            customer=cart.owner, cart=cart,
            content_type=request.initial_data['item']['content_type'],
            object_id=request.initial_data['item']['object'].id
        )
        request.initial_data['cart_item'] = {'cart_item': cart_item,
                                             'created': created}
        return view(request)
    return wrapper
