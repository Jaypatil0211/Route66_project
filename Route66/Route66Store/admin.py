from django.contrib import admin
from .models import Category, Brand, Product, HotWheelsCase, Order, OrderItem, Cart, CartItem, Review, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = Product
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'scale', 'price', 'stock', 'is_featured', 'is_new_arrival', 'is_treasure_hunt']
    list_filter = ['category', 'brand', 'scale', 'is_featured', 'is_new_arrival', 'is_treasure_hunt', 'is_super_treasure_hunt']
    search_fields = ['name', 'car_model', 'series']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_featured', 'is_new_arrival']


@admin.register(HotWheelsCase)
class HotWheelsCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'series_letter', 'price', 'cars_per_case', 'stock', 'is_featured']
    list_filter = ['year', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_featured']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'tracking_number']
    inlines = [OrderItemInline]
    list_editable = ['status']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'created_at']
    list_filter = ['rating']


admin.site.register(Cart)
admin.site.register(Wishlist)

# Customize admin site header
admin.site.site_header = '🏁 Route66 Diecast Admin'
admin.site.site_title = 'Route66 Admin'
admin.site.index_title = 'Route66 Management Panel'
