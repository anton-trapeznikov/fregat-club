from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from fregat.models import (
    Homepage, Media, MenuItem, Page, Pricelist, PricelistCategory, PriceItem,
    Redirect, Settings, Teaser
)
from mdeditor.widgets import MDEditorWidget


class PageMediaInline(admin.StackedInline):
    model = Media
    extra = 1
    fk_name = 'page'
    fields = (
        'image', 'youtube_url', 'caption', 'text',
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('heading', 'slug', 'is_published', 'updated_at', )
    list_filter = ('is_published', )
    search_fields = ('heading', 'content', 'slug', )
    prepopulated_fields = {'slug': ('heading', )}
    readonly_fields = ('updated_at', )
    inlines = (PageMediaInline, )

    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget},
    }

    fieldsets = (
        (None, {
            'fields': (
                'heading', 'slug', 'is_published', 'content', 'pricelist',
                'updated_at',
            )
        }),
        ('Метатеги', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('title', 'keywords', 'description', ),
        }),
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order_no', 'page', 'href', )
    list_filter = ('parent', )
    search_fields = ('name', )

    fieldsets = (
        (None, {
            'fields': ('name', 'parent', 'order_no', )
        }),
        ('Ссылка пункта меню', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('page', 'href', ),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = MenuItem.objects.filter(parent__isnull=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HomepageMediaInline(admin.StackedInline):
    model = Media
    extra = 1
    fk_name = 'homepage'
    fields = (
        'image', 'youtube_url', 'caption', 'text',
    )


@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'updated_at', )
    list_filter = ('is_published', )
    readonly_fields = ('updated_at', 'created_at', )
    inlines = (HomepageMediaInline, )
    exclude = ('hero_desktop_size', 'hero_tablet_size', 'hero_mobile_size', )
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget},
    }

    def title(self, obj):
        return 'Главная страница измененная %s' % obj.updated_at

    title.short_description = 'Объект'
    title.allow_tags = True

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at', 'is_active', )
    list_filter = ('is_active', )

    fieldsets = (
        ('Основные настройки', {
            'fields': (
                'is_active', 'phone', 'address', 'latitude',
                'longitude', 'add_yandex_reviews',
            )
        }),
        ('Описание организации для микроразметки', {
            'classes': ('collapse', ),
            'fields': (
                'organization_name', 'organization_description',
                'postal_code', 'region', 'city', 'street_address', 'email',
            ),
        }),
        ('Метатеги главной страницы', {
            'classes': ('collapse', ),
            'fields': (
                'homepage_title_pattern', 'homepage_keywords_pattern',
                'homepage_description_pattern',
            ),
        }),
        ('Метатеги списка новостей', {
            'classes': ('collapse', ),
            'fields': (
                'news_title_pattern', 'news_keywords_pattern',
                'news_description_pattern',
            ),
        }),
        ('Метатеги списка акций', {
            'classes': ('collapse', ),
            'fields': (
                'actions_title_pattern', 'actions_keywords_pattern',
                'actions_description_pattern',
            ),
        }),
        ('Метатеги текстовых страниц', {
            'classes': ('collapse', ),
            'fields': (
                'flatpage_title_pattern', 'flatpage_keywords_pattern',
                'flatpage_description_pattern',
            ),
        }),
        ('Метатеги по умолчанию', {
            'classes': ('collapse', ),
            'fields': (
                'default_title_pattern', 'default_keywords_pattern',
                'default_description_pattern',
            ),
        }),
        ('Инъекции в HTML', {
            'classes': ('collapse', ),
            'fields': (
                'head_injection', 'body_injection',
            ),
        }),
        ('robots.txt', {
            'classes': ('collapse', ),
            'fields': (
                'robots_txt',
            ),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = MenuItem.objects.filter(parent__isnull=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'created_at', )


@admin.register(Teaser)
class TeaserAdmin(admin.ModelAdmin):
    list_display = (
        'heading', 'preview', 'publish_date', 'is_published',
        'add_to_actions', 'add_to_news',
    )
    list_filter = (
        'is_published', 'add_to_actions', 'add_to_news',
    )
    readonly_fields = ('created_at', 'updated_at', )
    fields = (
        'is_published', 'heading', 'image', 'page', 'href',
        'add_to_actions', 'add_to_news',
        'order_no', 'publish_date', 'created_at', 'updated_at',
    )

    def preview(self, obj):
        return mark_safe('<img alt="" src="%s">' % obj.admin_thumbnail)

    preview.short_description = 'Превью'
    preview.allow_tags = True


@admin.register(Pricelist)
class PricelistAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_at', 'updated_at', )
    list_filter = ('is_default', )
    readonly_fields = ('created_at', 'updated_at', )
    fields = ('name', 'is_default', 'view', 'created_at', 'updated_at', )


@admin.register(PricelistCategory)
class PricelistCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_no', )
    fields = ('name', 'order_no', )


class PriceMediaInline(admin.StackedInline):
    model = Media
    extra = 1
    fk_name = 'price_item'
    fields = (
        'image', 'youtube_url', 'caption', 'text',
    )


@admin.register(PriceItem)
class PriceitemAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'preview', 'pricelist', 'category', 'common_price',
        'price_on_weekdays', 'price_on_weekend', 'price_on_holydays',
        'updated_at',
    )
    list_filter = ('pricelist', 'category', )
    readonly_fields = ('created_at', 'updated_at', )

    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget},
    }

    fieldsets = (
        ('Основные настройки', {
            'fields': (
                'pricelist', 'category', 'name', 'common_price',
                'price_on_weekdays', 'price_on_weekend', 'price_on_holydays',
                'unit', 'order_no',
            )
        }),
        ('Расширенное описание', {
            'classes': ('wide', 'extrapretty'),
            'fields': (
                'image', 'text',
            ),
        }),
    )

    inlines = (PriceMediaInline, )

    def preview(self, obj):
        return mark_safe('<img alt="" src="%s">' % obj.admin_thumbnail)

    preview.short_description = 'Превью'
    preview.allow_tags = True