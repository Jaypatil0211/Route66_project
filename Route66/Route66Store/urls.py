from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('cases/', views.cases_list, name='cases_list'),
    path('cases/<slug:slug>/', views.case_detail, name='case_detail'),
    path('search/', views.search, name='search'),
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/product/<int:product_id>/', views.add_to_cart, name='add_to_cart_product'),
    path('cart/add/case/<int:case_id>/', views.add_to_cart, name='add_to_cart_case'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    # Auth
    path('signup/', views.signup_view, name='signup'),
]
