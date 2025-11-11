# muzic56/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # صفحات اصلی
    path('', TemplateView.as_view(template_name="core/home.html"), name="home"),
    path('register/', TemplateView.as_view(template_name="core/register.html"), name="register"),
    path('login/', TemplateView.as_view(template_name="core/login.html"), name="login"),
    path('profile/', TemplateView.as_view(template_name="core/profile.html"), name="profile"),
    path('liked-songs/', TemplateView.as_view(template_name="core/liked_songs.html"), name="liked_songs"),
    path('my-playlists/', TemplateView.as_view(template_name="core/my_playlists.html"), name="my_playlists"),
    path('create-playlist/', TemplateView.as_view(template_name="core/create_playlist.html"), name="create_playlist"),
    path('playlist-detail/', TemplateView.as_view(template_name="core/playlist_detail.html"), name="playlist_detail"),
    path('search/', TemplateView.as_view(template_name="core/search.html"), name='search'),
    
    # اصلاح شده: اضافه کردن core/ به مسیر template
    path('public-playlists-search/', TemplateView.as_view(template_name='core/public_playlists_search.html'), name='public-playlists-search'),
    path('public-playlist-detail/', TemplateView.as_view(template_name='core/public_playlist_detail.html'), name='public-playlist-detail'),
    
    # API endpoints
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)