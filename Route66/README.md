# 🏁 Route66 — Diecast Legends

A Cars movie themed Django shopping website for diecast models, Hot Wheels cases, and collector's items.

## Project Structure

```
Route66/
├── Route66/          # Django project settings
├── store/            # Main app (products, cart, orders)
├── static/           # CSS, JS, images
├── templates/        # HTML templates
├── manage.py
├── seed_data.py      # Demo data loader
└── requirements.txt
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create superuser (admin)
```bash
python manage.py createsuperuser
```

### 4. Load demo data
```bash
python seed_data.py
```

### 5. Run the server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**
Admin: **http://127.0.0.1:8000/admin**

---

## Features

- 🛍️ **Full Shopping Experience** — Browse, filter, search, add to cart, checkout
- 🏎️ **Product Catalog** — Diecast models with scale, brand, year, color filters
- 📦 **Hot Wheels Cases** — Full case listings with details
- 🔥 **Treasure Hunts** — Special TH/Super TH badges and section
- ♥ **Wishlist** — Save favourite models
- ⭐ **Reviews** — Star ratings and written reviews
- 📋 **Order Tracking** — Full order history with status
- 🔐 **Authentication** — Signup, login, logout
- 🛠️ **Admin Panel** — Full product/order management

## Models

- `Product` — Diecast models with scale, brand, treasure hunt flags
- `HotWheelsCase` — Full case listings
- `Category` / `Brand` — Organization
- `Cart` / `CartItem` — Shopping cart
- `Order` / `OrderItem` — Order management
- `Review` — Product reviews
- `Wishlist` — User wishlists

## Theme

**Cars movie inspired** — Deep asphalt blacks, Route 66 red, checkered flag yellow. Typography uses Bebas Neue for display and Barlow Condensed for UI.

---

*"Life is a highway." 🏎️*
