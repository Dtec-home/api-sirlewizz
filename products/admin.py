from django.contrib import admin
from .models import Category, Product, ProductImage, Variant


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'featured', 'created_at')
    list_filter = ('category', 'featured')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, VariantInline]


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock', 'sku')
    list_filter = ('product__category',)
    search_fields = ('sku', 'product__name')
