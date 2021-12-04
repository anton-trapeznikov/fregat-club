from fregat.views import HomepageView, PageView, robots_txt, sitemap_xml
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView


favicon_view = RedirectView.as_view(
    url='/static/resources/favicon/favicon.ico',
    permanent=True
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('mdeditor/', include('mdeditor.urls')),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('favicon.ico', favicon_view),
    path('<slug>/', PageView.as_view(), name='page'),
    path('', HomepageView.as_view(), name='homepage'),
]

if settings and settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

handler404 = "fregat.views.h404"