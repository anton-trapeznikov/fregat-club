from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import condition
from django.views.generic import DetailView, TemplateView
from django.utils import timezone
from django.utils.decorators import method_decorator
from fregat.models import (
    Homepage, Media, Page, Pricelist, PricelistCategory,  PriceItem,
    Settings, Teaser,
)
from fregat.utils import to_int


class MediaViewMixin():
    def add_media(self, context, media_qs):
        paginator = Paginator(media_qs, 10)
        page = to_int(self.request.GET.get('media-page'), 1)
        page = min(max(page, 1), paginator.num_pages)
        media_list = paginator.get_page(page)
        context['media_list'] = media_list

        context['media_page_number'] = page
        context['media_pages'] = list(range(1, paginator.num_pages + 1))

        all_media = media_qs.only('youtube_url')
        youtube_urls = [m.youtube_url for m in all_media]

        context['has_photo'] = None in youtube_urls or '' in youtube_urls
        context['has_video'] = len(list(filter(None, youtube_urls))) > 0


def homepage_last_modified(request, *args, **kwargs):
    homepage = Homepage.objects.filter(is_published=True).first()
    return homepage.updated_at if homepage else None


class HomepageView(TemplateView, MediaViewMixin):
    @method_decorator(condition(last_modified_func=homepage_last_modified))
    def dispatch(self, request, *args, **kwargs):
        return super(HomepageView, self).dispatch(
            request, *args, **kwargs)

    template_name = "homepage.html"

    def add_content(self):
        homepage = Homepage.objects.filter(is_published=True).first()
        if not homepage:
            raise Http404()
        self.context['homepage'] = homepage
        self.object = homepage

    def add_metatags(self):
        self.request.metatag_data = {
            'whois': 'homepage',
        }

    def get_context_data(self, **kwargs):
        self.request.page_type = 'homepage'
        self.context = super(HomepageView, self).get_context_data(**kwargs)
        self.context['without_breadcrumbs'] = True

        self.add_content()
        self.add_media(self.context, Media.objects.filter(homepage=self.object))

        return self.context


def page_last_modified(request, slug):
    page = Page.objects.filter(slug=slug).first()
    return page.updated_at if page else None


class PageView(DetailView, MediaViewMixin):
    @method_decorator(condition(last_modified_func=page_last_modified))
    def dispatch(self, request, *args, **kwargs):
        return super(PageView, self).dispatch(
            request, *args, **kwargs)

    model = Page
    context_object_name = 'page'
    template_name = "page.html"

    def add_metatags(self):
        self.request.metatag_data = {
            'whois': 'flatpage',
            'title': self.object.title or self.object.heading,
            'keywords': self.object.keywords or self.object.heading,
            'description': self.object.description or self.object.heading,
        }

    def add_pricelist(self):
        pid = self.object.pricelist_id
        pricelist = Pricelist.objects.filter(pk=pid).first()
        prices = PriceItem.objects.filter(
            pricelist_id=pid
        ).select_related('category')

        media_map = {}
        for media in Media.objects.filter(price_item__in=prices):
            if media.price_item_id not in media_map:
                media_map[media.price_item_id] = []
            media_map[media.price_item_id].append(media)

        render_image_col = False
        for p in prices:
            p.media = media_map.get(p.pk, [])
            p.has_media = len(p.media) > 0
            p.has_extra = p.has_media and p.text

        self.context['pricelist'] = prices
        self.context['pricelist_view'] = pricelist.view if pricelist else None

    def get_context_data(self, **kwargs):
        self.request.page_type = 'flatpage'

        self.context = super(PageView, self).get_context_data(**kwargs)

        self.add_metatags()
        self.add_media(self.context, Media.objects.filter(page=self.object))

        if self.object.pricelist_id:
            self.add_pricelist()

        return self.context


def robots_txt(request):
    config = Settings.objects.filter(is_active=True).last()
    return HttpResponse(
        '%s\n' % config.robots_txt if config else '',
        content_type='text/plain'
    )


def sitemap_xml(request):
    entries = []

    content = render_to_string('sitemap.xml', {
        'entries': entries,
    })
    return HttpResponse(content, content_type='application/xml')


def h404(request, exception=None):
    request.page_type = '404'
    return render(request, '404.html', status=404)
