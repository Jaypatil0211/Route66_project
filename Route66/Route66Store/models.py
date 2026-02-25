from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('diecast_164', '1:64 Scale Diecast'),
        ('diecast_118', '1:18 Scale Diecast'),
        ('diecast_143', '1:43 Scale Diecast'),
        ('diecast_124', '1:24 Scale Diecast'),
        ('hotwheels_case', 'Hot Wheels Cases'),
        ('hotwheels_set', 'Hot Wheels Sets'),
        ('treasure_hunt', 'Treasure Hunts'),
        ('limited_edition', 'Limited Editions'),
        ('accessories', 'Accessories & Displays'),
        ('track_sets', 'Track Sets'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='diecast_164')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    SCALE_CHOICES = [
        ('1:18', '1:18'),
        ('1:24', '1:24'),
        ('1:43', '1:43'),
        ('1:64', '1:64'),
        ('N/A', 'N/A'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scale = models.CharField(max_length=10, choices=SCALE_CHOICES, default='1:64')
    car_model = models.CharField(max_length=100, blank=True, help_text="e.g. 1969 Camaro, Ford GT40")
    car_year = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, blank=True)
    series = models.CharField(max_length=100, blank=True, help_text="e.g. Hot Wheels Premium, Mainline")
    is_treasure_hunt = models.BooleanField(default=False)
    is_super_treasure_hunt = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def display_price(self):
        return self.sale_price if self.sale_price else self.price

    @property
    def discount_percent(self):
        if self.sale_price and self.price:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0


class HotWheelsCase(models.Model):
    """A full case of Hot Wheels (usually 72 cars per case)"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    year = models.IntegerField()
    series_letter = models.CharField(max_length=5, help_text="e.g. A, B, C, J")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cars_per_case = models.IntegerField(default=72)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cases/', blank=True, null=True)
    stock = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.year} Hot Wheels Case {self.series_letter} - {self.name}"

    def get_absolute_url(self):
        return reverse('store:case_detail', kwargs={'slug': self.slug})


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    case = models.ForeignKey(HotWheelsCase, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        item = self.product or self.case
        return f"{self.quantity}x {item} in Order #{self.order.id}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.cartitem_set.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.cartitem_set.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    case = models.ForeignKey(HotWheelsCase, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)

    @property
    def subtotal(self):
        item = self.product or self.case
        price = item.display_price if hasattr(item, 'display_price') else item.price
        return price * self.quantity

    @property
    def unit_price(self):
        item = self.product or self.case
        return item.display_price if hasattr(item, 'display_price') else item.price


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ by {self.user.username} on {self.product}"


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"
