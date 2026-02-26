from django.contrib import admin
from django import forms
from django.utils.text import slugify
from .models import Category, Brand, Product, HotWheelsCase, Order, OrderItem, Cart, CartItem, Review, Wishlist


def _unique_slug(model_cls, base_slug: str) -> str:
    base_slug = (base_slug or "").strip() or "item"
    slug = base_slug
    i = 2
    while model_cls.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{i}"
        i += 1
    return slug


class _SlugOptionalFormMixin(forms.ModelForm):
    """
    Admin UX: allow leaving slug empty; we auto-generate it.
    This avoids "Add/Change not working" cases where slug JS doesn't populate.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "slug" in self.fields:
            self.fields["slug"].required = False

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        name = (self.cleaned_data.get("name") or "").strip()
        if slug:
            return slugify(slug)
        if name:
            return slugify(name)
        return slug



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    form = type("CategoryAdminForm", (_SlugOptionalFormMixin,), {"Meta": type("Meta", (), {"model": Category, "fields": "__all__"})})

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = _unique_slug(Category, slugify(obj.name))
        super().save_model(request, obj, form, change)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    form = type("BrandAdminForm", (_SlugOptionalFormMixin,), {"Meta": type("Meta", (), {"model": Brand, "fields": "__all__"})})

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = _unique_slug(Brand, slugify(obj.name))
        super().save_model(request, obj, form, change)


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
    form = type("ProductAdminForm", (_SlugOptionalFormMixin,), {"Meta": type("Meta", (), {"model": Product, "fields": "__all__"})})

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = _unique_slug(Product, slugify(obj.name))
        super().save_model(request, obj, form, change)


@admin.register(HotWheelsCase)
class HotWheelsCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'series_letter', 'price', 'cars_per_case', 'stock', 'is_featured']
    list_filter = ['year', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_featured']
    form = type("HotWheelsCaseAdminForm", (_SlugOptionalFormMixin,), {"Meta": type("Meta", (), {"model": HotWheelsCase, "fields": "__all__"})})

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = _unique_slug(HotWheelsCase, slugify(obj.name))
        super().save_model(request, obj, form, change)


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
