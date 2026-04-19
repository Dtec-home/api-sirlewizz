from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Category, Product, Variant, ProductImage
import urllib.request

CATEGORIES = [
    ('Headwear', 'headwear'),
    ('Tops', 'tops'),
    ('Outerwear', 'outerwear'),
    ('Bottoms', 'bottoms'),
    ('Underwear', 'underwear'),
    ('Socks', 'socks'),
    ('Accessories', 'accessories'),
    ('Footwear', 'footwear'),
]

# (name, category_slug, price, featured, description, image_url, variants: [(size, color, stock)])
PRODUCTS = [
    (
        'Classic Oxford Shirt',
        'tops', 2800, True,
        'Premium Oxford cloth shirt with a tailored fit. Perfect for business casual or smart casual occasions.',
        'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&q=80',
        [('S','White',18),('M','White',22),('L','White',15),('XL','White',10),
         ('S','Blue',12),('M','Blue',20),('L','Blue',14),('XL','Blue',8),
         ('M','Black',16),('L','Black',12)],
    ),
    (
        'Slim Fit Chinos',
        'bottoms', 3500, True,
        'Versatile slim fit chinos in premium cotton blend. Pairs well with shirts and polos.',
        'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&q=80',
        [('30','Khaki',10),('32','Khaki',14),('34','Khaki',8),('36','Khaki',6),
         ('30','Navy',8),('32','Navy',12),('34','Navy',10),
         ('32','Olive',9),('34','Olive',7),('36','Olive',4)],
    ),
    (
        'Leather Derby Shoes',
        'footwear', 8500, True,
        'Classic full-grain leather derby shoes with a rubber sole. Handcrafted for durability and style.',
        'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&q=80',
        [('40','Black',6),('41','Black',8),('42','Black',10),('43','Black',7),('44','Black',4),
         ('40','Brown',5),('41','Brown',7),('42','Brown',9),('43','Brown',6)],
    ),
    (
        'Wool Blazer',
        'outerwear', 12000, True,
        'Fine Italian wool blazer with a modern slim cut. Ideal for formal events and office wear.',
        'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80',
        [('S','Charcoal',4),('M','Charcoal',6),('L','Charcoal',5),('XL','Charcoal',3),
         ('S','Navy',3),('M','Navy',5),('L','Navy',4),('XL','Navy',2)],
    ),
    (
        'Snapback Cap',
        'headwear', 1200, True,
        'Structured snapback cap with embroidered logo. One size fits all with adjustable snap closure.',
        'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800&q=80',
        [('One Size','Black',30),('One Size','Mustard',20),('One Size','White',25),('One Size','Navy',18)],
    ),
    (
        'Premium Boxer Briefs 3-Pack',
        'underwear', 1800, False,
        'Soft modal-cotton blend boxer briefs. Breathable, comfortable, and long-lasting.',
        'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=800&q=80',
        [('S','Black',20),('M','Black',25),('L','Black',20),('XL','Black',15),
         ('S','Grey',18),('M','Grey',22),('L','Grey',18),
         ('M','Navy',20),('L','Navy',16)],
    ),
    (
        'Silk Tie',
        'accessories', 2200, False,
        '100% pure silk tie with a classic woven pattern. Adds a refined touch to any formal outfit.',
        'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&q=80',
        [('One Size','Burgundy',15),('One Size','Navy',18),('One Size','Mustard',12),('One Size','Black',20)],
    ),
    (
        'Ankle Socks 5-Pack',
        'socks', 900, False,
        'Cushioned ankle socks in a breathable cotton blend. Reinforced heel and toe for durability.',
        'https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=800&q=80',
        [('One Size','Black',40),('One Size','White',35),('One Size','Mixed',30)],
    ),
    (
        'Polo Shirt',
        'tops', 2200, True,
        'Classic piqué polo shirt with a two-button placket. A wardrobe essential for smart casual looks.',
        'https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=800&q=80',
        [('S','White',15),('M','White',20),('L','White',18),('XL','White',10),
         ('S','Black',12),('M','Black',18),('L','Black',14),
         ('M','Navy',16),('L','Navy',12)],
    ),
    (
        'Hoodie',
        'tops', 3800, True,
        'Heavyweight fleece hoodie with a kangaroo pocket and adjustable drawstring hood.',
        'https://images.unsplash.com/photo-1509942774463-acf339cf87d5?w=800&q=80',
        [('S','Black',10),('M','Black',15),('L','Black',12),('XL','Black',8),
         ('M','Grey',14),('L','Grey',10),('XL','Grey',6),
         ('M','Mustard',8),('L','Mustard',6)],
    ),
    (
        'Slim Fit Jeans',
        'bottoms', 4200, True,
        'Premium stretch denim jeans with a slim tapered fit. Comfortable enough for all-day wear.',
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80',
        [('30','Indigo',8),('32','Indigo',12),('34','Indigo',10),('36','Indigo',6),
         ('30','Black',7),('32','Black',10),('34','Black',8),('36','Black',5)],
    ),
    (
        'Leather Belt',
        'accessories', 1500, False,
        'Full-grain leather belt with a brushed silver buckle. Available in multiple sizes.',
        'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&q=80',
        [('S','Black',20),('M','Black',25),('L','Black',20),('XL','Black',15),
         ('M','Brown',18),('L','Brown',15),('XL','Brown',10)],
    ),
    (
        'White Sneakers',
        'footwear', 5500, True,
        'Clean minimalist leather sneakers with a cushioned insole. Versatile enough for any casual outfit.',
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',
        [('40','White',8),('41','White',10),('42','White',12),('43','White',9),('44','White',6),
         ('41','Black',7),('42','Black',9),('43','Black',8)],
    ),
    (
        'Crew Neck Sweatshirt',
        'tops', 3200, False,
        'Soft fleece crew neck sweatshirt. Relaxed fit with ribbed cuffs and hem.',
        'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800&q=80',
        [('S','Grey',12),('M','Grey',16),('L','Grey',14),('XL','Grey',8),
         ('M','Black',14),('L','Black',10),
         ('M','Navy',10),('L','Navy',8)],
    ),
    (
        'Formal Trousers',
        'bottoms', 4500, False,
        'Tailored formal trousers in a wool-blend fabric. Features a flat front and straight leg cut.',
        'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800&q=80',
        [('30','Charcoal',6),('32','Charcoal',8),('34','Charcoal',7),('36','Charcoal',4),
         ('30','Black',5),('32','Black',7),('34','Black',6),('36','Black',3)],
    ),
    (
        'Bucket Hat',
        'headwear', 1400, False,
        'Cotton twill bucket hat with a wide brim. Lightweight and packable for travel.',
        'https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=800&q=80',
        [('One Size','Black',22),('One Size','Khaki',18),('One Size','Olive',15)],
    ),
    (
        'Loafers',
        'footwear', 7200, False,
        'Slip-on leather loafers with a penny strap detail. Smart casual footwear for any occasion.',
        'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&q=80',
        [('40','Black',5),('41','Black',7),('42','Black',8),('43','Black',6),('44','Black',4),
         ('41','Brown',6),('42','Brown',7),('43','Brown',5)],
    ),
    (
        'Crew Socks 3-Pack',
        'socks', 750, False,
        'Mid-calf crew socks in a soft cotton blend. Ribbed top for a secure fit.',
        'https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=800&q=80',
        [('One Size','Black',35),('One Size','White',30),('One Size','Navy',25)],
    ),
    (
        'Leather Wallet',
        'accessories', 2800, False,
        'Slim bifold wallet in full-grain leather. Features 6 card slots and a bill compartment.',
        'https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80',
        [('One Size','Black',20),('One Size','Brown',18),('One Size','Tan',12)],
    ),
    (
        'Denim Jacket',
        'outerwear', 6500, True,
        'Classic denim jacket with a slightly oversized fit. Features chest pockets and button closure.',
        'https://images.unsplash.com/photo-1601333144130-8cbb312386b6?w=800&q=80',
        [('S','Indigo',6),('M','Indigo',8),('L','Indigo',7),('XL','Indigo',4),
         ('M','Black',6),('L','Black',5),('XL','Black',3)],
    ),
]


def fetch_image(url: str, filename: str):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return ContentFile(resp.read(), name=filename)
    except Exception as e:
        return None


class Command(BaseCommand):
    help = 'Seed categories and products with real images from Unsplash'

    def add_arguments(self, parser):
        parser.add_argument('--no-images', action='store_true', help='Skip image downloads')
        parser.add_argument('--add-images', action='store_true', help='Backfill images on existing products')

    def handle(self, *args, **options):
        skip_images = options['no_images']
        add_images = options['add_images']

        # Categories
        cats = {}
        for name, slug in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cats[slug] = cat

        self.stdout.write(f'  {len(cats)} categories ready')

        # Products
        from django.utils.text import slugify
        created_count = 0

        for name, cat_slug, price, featured, description, image_url, variants in PRODUCTS:
            product, created = Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    'name': name,
                    'category': cats[cat_slug],
                    'price': price,
                    'featured': featured,
                    'description': description,
                },
            )

            if created or (add_images and not product.images.exists()):
                # Variants (only on new products)
                if created:
                    for size, color, stock in variants:
                        Variant.objects.get_or_create(
                            product=product, size=size, color=color,
                            defaults={'stock': stock}
                        )

                # Image
                if not skip_images:
                    filename = f"{product.slug}.jpg"
                    image_file = fetch_image(image_url, filename)
                    if image_file:
                        ProductImage.objects.create(product=product, image=image_file, order=0)
                        self.stdout.write(f'  ✓ {name}')
                    else:
                        self.stdout.write(self.style.WARNING(f'  ✗ {name} (image failed)'))
                else:
                    self.stdout.write(f'  ✓ {name} (no image)')

                created_count += 1
            else:
                self.stdout.write(f'  ~ {name} (exists, skipped)')

        self.stdout.write(self.style.SUCCESS(f'\nDone. {created_count} new products created.'))
