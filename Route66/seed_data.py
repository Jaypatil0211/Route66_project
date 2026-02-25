"""
Run this after migrations to seed demo data:
python seed_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Route66.settings')
django.setup()

from store.models import Category, Brand, Product, HotWheelsCase
from django.utils.text import slugify

# Brands
brands_data = [
    'Hot Wheels', 'Matchbox', 'Maisto', 'Bburago', 'Tomica',
    'Greenlight', 'Auto World', 'Johnny Lightning', 'M2 Machines',
]
brands = {}
for b in brands_data:
    obj, _ = Brand.objects.get_or_create(name=b, defaults={'slug': slugify(b)})
    brands[b] = obj
print(f"✅ {len(brands)} brands created")

# Categories
cats_data = [
    ('1:64 Scale Diecast', 'diecast_164', '164-scale-diecast'),
    ('1:18 Scale Diecast', 'diecast_118', '118-scale-diecast'),
    ('1:43 Scale Diecast', 'diecast_143', '143-scale-diecast'),
    ('1:24 Scale Diecast', 'diecast_124', '124-scale-diecast'),
    ('Hot Wheels Cases', 'hotwheels_case', 'hotwheels-cases'),
    ('Treasure Hunts', 'treasure_hunt', 'treasure-hunts'),
    ('Limited Editions', 'limited_edition', 'limited-editions'),
    ('Track Sets', 'track_sets', 'track-sets'),
    ('Display Accessories', 'accessories', 'display-accessories'),
]
categories = {}
for name, ctype, slug in cats_data:
    obj, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'category_type': ctype})
    categories[name] = obj
print(f"✅ {len(categories)} categories created")

# Products
products_data = [
    # (name, brand, category_name, scale, car_model, year, color, series, price, stock, is_featured, is_new, is_th)
    ("'69 Camaro Z/28", 'Hot Wheels', '1:64 Scale Diecast', '1:64', '1969 Chevrolet Camaro Z/28', 1969, 'Orange', 'Hot Wheels Classics', 149, 25, True, True, False),
    ("Ford GT40 Mk. I", 'Hot Wheels', '1:64 Scale Diecast', '1:64', 'Ford GT40 Mk. I', 1966, 'Gulf Blue', 'Hot Wheels Premium', 299, 15, True, True, False),
    ("'70 Dodge Charger R/T", 'Hot Wheels', '1:64 Scale Diecast', '1:64', '1970 Dodge Charger R/T', 1970, 'Black', 'Hot Wheels Mainline', 99, 40, True, False, False),
    ("Porsche 911 GT3 RS", 'Hot Wheels', '1:64 Scale Diecast', '1:64', 'Porsche 911 GT3 RS', 2023, 'Gulf Orange', 'Hot Wheels Car Culture', 349, 8, True, True, False),
    ("Ferrari 250 GTO", 'Hot Wheels', 'Treasure Hunts', '1:64', 'Ferrari 250 GTO', 1962, 'Red', 'Hot Wheels Premium', 599, 5, True, False, True),
    ("Lamborghini Countach", 'Matchbox', '1:64 Scale Diecast', '1:64', 'Lamborghini Countach LP400', 1974, 'Yellow', 'Matchbox Moving Parts', 199, 20, False, True, False),
    ("Ford Mustang GT500", 'Maisto', '1:18 Scale Diecast', '1:18', '2020 Ford Mustang GT500', 2020, 'Shadow Black', 'Maisto Special Edition', 2499, 6, True, False, False),
    ("Chevrolet Corvette C8", 'Bburago', '1:18 Scale Diecast', '1:18', '2020 Chevrolet Corvette C8', 2020, 'Torch Red', 'Bburago Signature', 1999, 4, True, True, False),
    ("Toyota Supra A80", 'Tomica', '1:64 Scale Diecast', '1:64', '1993 Toyota Supra A80', 1993, 'White', 'Tomica Limited Vintage', 449, 12, False, False, False),
    ("'67 Shelby GT500", 'Greenlight', '1:43 Scale Diecast', '1:43', '1967 Shelby GT500', 1967, 'Dark Highland Green', 'Greenlight Hollywood', 799, 7, True, False, False),
    ("McLaren Senna", 'Hot Wheels', '1:64 Scale Diecast', '1:64', 'McLaren Senna', 2018, 'Orange', 'Hot Wheels Exotics', 249, 18, False, True, False),
    ("Bugatti Chiron", 'Bburago', '1:24 Scale Diecast', '1:24', 'Bugatti Chiron', 2019, 'Blue/Black', 'Bburago Street Fire', 1299, 9, True, False, False),
    ("Nissan Skyline GT-R R34", 'Hot Wheels', 'Treasure Hunts', '1:64', 'Nissan Skyline GT-R R34', 1999, 'Bayside Blue', 'Fast & Furious Premium', 899, 3, True, True, True),
    ("Delorean DMC-12", 'Hot Wheels', 'Limited Editions', '1:64', 'DeLorean DMC-12', 1981, 'Brushed Metal', 'Back to the Future', 499, 10, True, False, False),
    ("Aston Martin DB5", 'Matchbox', '1:43 Scale Diecast', '1:43', 'Aston Martin DB5', 1964, 'Silver Birch', 'James Bond Collection', 699, 8, False, False, False),
    ("Volkswagen Beetle", 'Maisto', '1:18 Scale Diecast', '1:18', '1967 Volkswagen Beetle', 1967, 'Sky Blue', 'Maisto Classic', 1799, 5, False, True, False),
]

created = 0
for pdata in products_data:
    name, bname, cname, scale, car_model, year, color, series, price, stock, featured, new_arr, is_th = pdata
    slug = slugify(name)
    if Product.objects.filter(slug=slug).exists():
        continue
    Product.objects.create(
        name=name,
        slug=slug,
        brand=brands.get(bname),
        category=categories.get(cname),
        scale=scale,
        car_model=car_model,
        car_year=year,
        color=color,
        series=series,
        price=price,
        stock=stock,
        is_featured=featured,
        is_new_arrival=new_arr,
        is_treasure_hunt=is_th,
        description=f"A stunning {scale} scale diecast model of the {year} {car_model}. "
                    f"Part of the {series} series. Finished in {color}. "
                    f"Perfect for collectors and enthusiasts. Die-cast metal body with detailed interior."
    )
    created += 1

print(f"✅ {created} products created")

# Hot Wheels Cases
cases_data = [
    ("2025 Hot Wheels Mainline Case A", 2025, "A", 2499, 72, "Full 2025 Case A — 72 assorted Hot Wheels cars"),
    ("2025 Hot Wheels Mainline Case B", 2025, "B", 2499, 72, "Full 2025 Case B — 72 assorted Hot Wheels cars"),
    ("2024 Hot Wheels Premium Car Culture Case", 2024, "P", 4999, 10, "10-car Car Culture assortment — themed collection"),
    ("2025 Hot Wheels Collector Case", 2025, "C", 3499, 48, "Collector edition case with chase vehicles"),
    ("2024 Hot Wheels Fast & Furious Premium Case", 2024, "F", 5499, 10, "Fast & Furious premium case — 10 premium models"),
]
for name, year, letter, price, count, desc in cases_data:
    slug = slugify(name)
    HotWheelsCase.objects.get_or_create(slug=slug, defaults={
        'name': name, 'year': year, 'series_letter': letter,
        'price': price, 'cars_per_case': count, 'description': desc,
        'stock': 15, 'is_featured': True
    })
print(f"✅ {len(cases_data)} HW cases created")

print("\n🏁 Route66 seed data loaded successfully!")
print("   Run: python manage.py createsuperuser to create admin")
