from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from .models import Product, Category, Brand, HotWheelsCase, Cart, CartItem, Order, OrderItem, Review, Wishlist
from .forms import SignUpForm, ReviewForm, CheckoutForm


def home(request):
    featured_products = Product.objects.filter(is_featured=True, stock__gt=0)[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True, stock__gt=0)[:8]
    treasure_hunts = Product.objects.filter(is_treasure_hunt=True, stock__gt=0)[:4]
    featured_cases = HotWheelsCase.objects.filter(is_featured=True, stock__gt=0)[:3]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'treasure_hunts': treasure_hunts,
        'featured_cases': featured_cases,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products = Product.objects.filter(stock__gt=0)
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    scale = request.GET.get('scale', '')
    sort = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    is_treasure_hunt = request.GET.get('is_treasure_hunt', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(car_model__icontains=query) |
            Q(description__icontains=query) | Q(series__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if scale:
        products = products.filter(scale=scale)
    if is_treasure_hunt:
        products = products.filter(is_treasure_hunt=True)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_map = {
        'price_asc': 'price', 'price_desc': '-price',
        'name': 'name', '-created_at': '-created_at', 'popular': '-id',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    categories = Category.objects.all()
    brands = Brand.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'query': query,
        'selected_category': category_slug,
        'selected_scale': scale,
        'sort': sort,
        'is_treasure_hunt': is_treasure_hunt,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = wishlist.products.filter(id=product.id).exists()

    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            r = review_form.save(commit=False)
            r.product = product
            r.user = request.user
            r.save()
            messages.success(request, 'Review submitted!')
            return redirect('store:product_detail', slug=slug)

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related': related,
        'in_wishlist': in_wishlist,
        'review_form': review_form,
    }
    return render(request, 'store/product_detail.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, stock__gt=0)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})


def cases_list(request):
    cases = HotWheelsCase.objects.filter(stock__gt=0)
    return render(request, 'store/cases_list.html', {'cases': cases})


def case_detail(request, slug):
    case = get_object_or_404(HotWheelsCase, slug=slug)
    return render(request, 'store/case_detail.html', {'case': case})


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.select_related('product', 'case').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})


@login_required
def add_to_cart(request, product_id=None, case_id=None):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, case=None)
    elif case_id:
        case = get_object_or_404(HotWheelsCase, id=case_id)
        item, created = CartItem.objects.get_or_create(cart=cart, case=case, product=None)
    else:
        messages.error(request, 'Invalid item.')
        return redirect('store:home')

    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, 'Added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'store:cart'))


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Removed from cart.')
    return redirect('store:cart')


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'],
                notes=form.cleaned_data.get('notes', ''),
            )
            for ci in items:
                OrderItem.objects.create(
                    order=order,
                    product=ci.product,
                    case=ci.case,
                    quantity=ci.quantity,
                    price=ci.unit_price,
                )
            order.calculate_total()
            items.delete()
            messages.success(request, f'Order #{order.id} placed successfully! 🏁')
            return redirect('store:order_detail', order_id=order.id)
    else:
        form = CheckoutForm()
    return render(request, 'store/checkout.html', {'cart': cart, 'items': items, 'form': form})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist': wishlist})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if wishlist.products.filter(id=product_id).exists():
        wishlist.products.remove(product)
        messages.info(request, 'Removed from wishlist.')
    else:
        wishlist.products.add(product)
        messages.success(request, 'Added to wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'store:wishlist'))


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Route66, {user.username}!')
            return redirect('store:home')
    else:
        form = SignUpForm()
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    """Custom login view that fires a success toast on login."""
    if request.user.is_authenticated:
        return redirect('store:home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! You are now logged in.')
            next_url = request.GET.get('next', '') or request.POST.get('next', '')
            return redirect(next_url if next_url else 'store:home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Custom logout view that fires an info toast after logout."""
    username = request.user.username if request.user.is_authenticated else ''
    logout(request)
    if username:
        messages.info(request, f'You have been logged out successfully. See you soon, {username}!')
    return redirect('store:home')


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(car_model__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.none()
    cases = HotWheelsCase.objects.filter(name__icontains=query) if query else HotWheelsCase.objects.none()
    return render(request, 'store/search_results.html', {
        'query': query, 'products': products, 'cases': cases
    })
