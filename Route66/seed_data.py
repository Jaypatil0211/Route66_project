"""
Run this after migrations to seed demo data:
python seed_data.py
"""
import os, django, requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Route66.settings')
django.setup()

from Route66Store.models import Category, Brand, Product, HotWheelsCase
from django.core.files.base import ContentFile
from django.utils.text import slugify

# ─── Brands (ONLY Hot Wheels, Bburago, CCA) ──────────────────────────────────
brands_data = ['Hot Wheels', 'CCA', 'Bburago']
brands = {}
for b in brands_data:
    obj, _ = Brand.objects.get_or_create(name=b, defaults={'slug': slugify(b)})
    brands[b] = obj

# Remove any extra brands that are not in the allowed list
from Route66Store.models import Brand as BrandModel
extra_brands = BrandModel.objects.exclude(slug__in=[slugify(b) for b in brands_data])
for brand in extra_brands:
    # Reassign products of this brand before deleting
    products_to_reassign = Product.objects.filter(brand=brand)
    for i, prod in enumerate(products_to_reassign):
        reassign_to = brands_data[i % len(brands_data)]
        prod.brand = brands[reassign_to]
        prod.save(update_fields=['brand'])
        print(f"  -> Reassigned '{prod.name}' from '{brand.name}' -> '{reassign_to}'")
    brand.delete()
    print(f"  [DELETED] Brand: {brand.name}")

print(f"[OK] {len(brands)} brands ready: {list(brands.keys())}")

# ─── Categories ───────────────────────────────────────────────────────────────
cats_data = [
    ('1:64 Scale Diecast', 'diecast_164', '164-scale-diecast'),
    ('1:18 Scale Diecast', 'diecast_118', '118-scale-diecast'),
    ('1:43 Scale Diecast', 'diecast_143', '143-scale-diecast'),
    ('1:24 Scale Diecast', 'diecast_124', '124-scale-diecast'),
    ('Hot Wheels Cases',   'hotwheels_case', 'hotwheels-cases'),
    ('Treasure Hunts',     'treasure_hunt', 'treasure-hunts'),
    ('Limited Editions',   'limited_edition', 'limited-editions'),
    ('Track Sets',         'track_sets', 'track-sets'),
    ('Display Accessories','accessories', 'display-accessories'),
]
categories = {}
for name, ctype, slug in cats_data:
    obj, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'category_type': ctype})
    categories[name] = obj
print(f"[OK] {len(categories)} categories ready")

# ─── Products ─────────────────────────────────────────────────────────────────
# (name, brand, category_name, scale, car_model, year, color, series, price, stock, is_featured, is_new, is_th)
# NOTE: All brands are ONLY 'Hot Wheels', 'CCA', or 'Bburago'
products_data = [
    ("BMW M3 Competition",      'CCA',        '1:18 Scale Diecast', '1:18', 'BMW M3 Competition',      2021, 'Isle of Men Green',  'CCA Special Edition',  2499,  6, True,  False, False),
    ("Lamborghini Huracan STO", 'CCA',        '1:24 Scale Diecast', '1:24', 'Lamborghini Huracan STO', 2021, 'Yellow',             'CCA Signature Series', 1499, 10, True,  True,  False),
    ("Ford Mustang GT500",      'Hot Wheels', '1:64 Scale Diecast', '1:64', 'Ford Mustang GT500',      2020, 'Dark Highland Green','Hot Wheels Mainline',   799,  7, True,  False, False),
    ("Ferrari 250 GTO",         'Hot Wheels', 'Treasure Hunts',     '1:64', 'Ferrari 250 GTO',         1962, 'Red',                'Hot Wheels Premium',    599,  5, True,  False, True),
    ("Bugatti Chiron",          'Bburago',    '1:24 Scale Diecast', '1:24', 'Bugatti Chiron',          2019, 'Blue/Black',         'Bburago Street Fire',  1299,  9, True,  False, False),
    ("Volkswagen Beetle",       'Bburago',    '1:18 Scale Diecast', '1:18', '1967 Volkswagen Beetle',  1967, 'Sky Blue',           'Bburago Classic',      1799,  5, False, True,  False),
]

# Delete products NOT in the keep list
KEEP_NAMES = [p[0] for p in products_data]
removed = Product.objects.exclude(name__in=KEEP_NAMES).delete()
print(f"[CLEANUP] Removed {removed[0]} old products not in the keep list")

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
        description=(
            f"A stunning {scale} scale diecast model of the {year} {car_model}. "
            f"Part of the {series} series. Finished in {color}. "
            f"Perfect for collectors and enthusiasts. Die-cast metal body with detailed interior."
        )
    )
    created += 1

print(f"[OK] {created} new products created")

# ─── Assign Images to Products ────────────────────────────────────────────────
# Map keywords (lowercase) to stable, working image URLs
IMAGE_MAP = {
    "bmw":         "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
    "lamborghini": "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800",
    "mustang":     "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=800",
    "ferrari":     "https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=800",
    "bugatti":     "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800",
    "volkswagen":  "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800",
    "beetle":      "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800",
}
FALLBACK_URL = "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_image_url(product_name: str) -> str:
    name_lower = product_name.lower()
    for keyword, url in IMAGE_MAP.items():
        if keyword in name_lower:
            return url
    return FALLBACK_URL

def download_image(url: str, filename: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        ext = 'jpg'
        if 'png' in resp.headers.get('Content-Type', ''):
            ext = 'png'
        fname = f"{filename}.{ext}"
        return ContentFile(resp.content, name=fname)
    except Exception as e:
        print(f"    [WARN] Download failed: {e}")
        return None

print("\n[IMAGES] Assigning images to products...")
for product in Product.objects.all():
    if product.image:
        print(f"  [SKIP] '{product.name}' already has image")
        continue
    url = get_image_url(product.name)
    print(f"  [DL] '{product.name}' -> downloading...")
    img = download_image(url, slugify(product.name))
    if img:
        product.image.save(img.name, img, save=True)
        print(f"  [SAVED] Image saved for '{product.name}'")
    else:
        print(f"  [FAIL] No image for '{product.name}'")

# ─── Hot Wheels Cases ─────────────────────────────────────────────────────────
cases_data = [
    ("2025 Hot Wheels Mainline Case A",        2025, "A", 2499, 72, "Full 2025 Case A — 72 assorted Hot Wheels cars"),
    ("2025 Hot Wheels Mainline Case B",        2025, "B", 2499, 72, "Full 2025 Case B — 72 assorted Hot Wheels cars"),
    ("2024 Hot Wheels Premium Car Culture Case",2024, "P", 4999, 10, "10-car Car Culture assortment — themed collection"),
    ("2025 Hot Wheels Collector Case",         2025, "C", 3499, 48, "Collector edition case with chase vehicles"),
    ("2024 Hot Wheels Fast & Furious Premium Case", 2024, "F", 5499, 10, "Fast & Furious premium case — 10 premium models"),
]
for name, year, letter, price, count, desc in cases_data:
    slug = slugify(name)
    HotWheelsCase.objects.get_or_create(slug=slug, defaults={
        'name': name, 'year': year, 'series_letter': letter,
        'price': price, 'cars_per_case': count, 'description': desc,
        'stock': 15, 'is_featured': True
    })
print(f"[OK] {len(cases_data)} HW cases ready")

print("\n[DONE] Route66 seed data loaded successfully!")
print(f"   Brands: {list(Brand.objects.values_list('name', flat=True))}")
print(f"   Products with images: {Product.objects.exclude(image='').count()} / {Product.objects.count()}")
print("   Run: python manage.py createsuperuser  to create admin")
