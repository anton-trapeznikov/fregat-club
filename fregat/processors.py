from django.template.loader import render_to_string
from django.utils import timezone
from fregat.models import MenuItem, Settings, Teaser
from fregat.utils import to_float


def main_menu_processor(request):
    items = MenuItem.objects.all().select_related('page')

    parent_map = {}
    for i in items:
        i.url = i.page.get_absolute_url() if i.page else i.href
        if i.parent_id:
            if i.parent_id not in parent_map:
                parent_map[i.parent_id] = []
            parent_map[i.parent_id].append(i)

    menu = []
    for i in items:
        if i.parent_id is None:
            i.children = parent_map.get(i.pk)
            menu.append(i)

    return {
        'main_menu': menu,
    }


def canonical_processor(request):
    gets = {}
    for key in request.GET:
        gets[key] = request.GET.getlist(key)

    canonical = request.build_absolute_uri('?') if gets.keys() else ''
    meta_robots_noindex = False

    if 'page' in gets:
        meta_robots_noindex = True
        canonical = ''

    return {
        'rel_canonical': canonical,
        'meta_robots_noindex': meta_robots_noindex,
    }


def settings_processor(request):
    metatag_data = getattr(request, 'metatag_data', {})
    config = Settings.objects.filter(is_active=True).last()
    request.site_config = config
    page_type = getattr(request, 'page_type', 'default')
    without_breadcrumbs_types = ('homepage', 'default')

    context = {
        'config': config,
        'metatag': {},
        'page_type': page_type,
        'without_breadcrumbs': page_type in without_breadcrumbs_types,
    }

    if config:
        whois = metatag_data.get('whois', 'default')

        title = getattr(
            config,
            '%s_title_pattern' % whois,
            getattr(config, 'default_title_pattern', '')
        )

        keywords = getattr(
            config,
            '%s_keywords_pattern' % whois,
            getattr(config, 'default_keywords_pattern', '')
        )

        description = getattr(
            config,
            '%s_description_pattern' % whois,
            getattr(config, 'default_description_pattern', '')
        )

        context['metatag'] = {}
        context['metatag']['title'] = title.replace(
            '__V__',
            metatag_data.get('title', '')
        )
        context['metatag']['keywords'] = keywords.replace(
            '__V__',
            metatag_data.get('keywords', '')
        )
        context['metatag']['description'] = description.replace(
            '__V__',
            metatag_data.get('description', '')
        )

        request.front_data['contacts']['address'] = config.street_address
        request.front_data['contacts']['phone'] = config.phone

        prices = []
        prices = [p for p in prices if p]
        price_range = [min(prices), max(prices)] if prices else []

        context['json_ld'] = render_to_string('json_ld.template', {
            'config': config,
            'price_range': price_range,
        })

        latitude = to_float(config.latitude)
        longitude = to_float(config.longitude)

        if latitude and longitude:
            request.front_data['geo']['latitude'] = latitude
            request.front_data['geo']['longitude'] = longitude
            context['has_geo_coordinates'] = True
            context['geo_data'] = request.front_data['geo']

    return context


def front_data_processor(request):
    return {'front_data': request.front_data}


def teasers_processor(request):
    now = timezone.now().date()
    actions = Teaser.objects.filter(
        add_to_actions=True,
        is_published=True,
        publish_date__lte=now,
    ).select_related('page')

    news = Teaser.objects.filter(
        add_to_news=True,
        is_published=True,
        publish_date__lte=now,
    ).select_related('page')[:1]

    return {'actions': actions, 'news': news}