# core/urls.py
from django.urls import path
from . import views
from .views import (
    RegisterView, LoginView, UserProfileView, MusicUploadView, MusicListView, 
    LogoutView, LikeMusicView, LikedMusicView, PlaylistListView, CreatePlaylistView,
    AddToPlaylistView, GetUserPlaylistsView, CreatePlaylistPageView, 
    CreatePlaylistFinalView, PlaylistDetailView, DeletePlaylistView, RemoveSongFromPlaylistView,
    PublicPlaylistsView,
    PopularMusicView, SearchMusicView, DeleteAccountView, DeleteMusicView,
)

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    
    path('music/upload/', MusicUploadView.as_view(), name='music-upload'),
    path('music/list/', MusicListView.as_view(), name='music-list'),
    path('music/<int:music_id>/like/', LikeMusicView.as_view(), name='like-music'),
    path('music/liked/', LikedMusicView.as_view(), name='liked-music'),
    path('music/<int:music_id>/delete/', DeleteMusicView.as_view(), name='delete-music'),
    
    
    path('music/popular/', PopularMusicView.as_view(), name='popular-music'),
    path('music/search/', SearchMusicView.as_view(), name='search-music'),
    
    
    path('playlists/', PlaylistListView.as_view(), name='playlist-list'),
    path('playlists/create/', CreatePlaylistView.as_view(), name='create-playlist'),
    path('playlists/add-song/', AddToPlaylistView.as_view(), name='add-to-playlist'),
    path('playlists/user-playlists/', GetUserPlaylistsView.as_view(), name='user-playlists'),
    path('playlists/create-page/', CreatePlaylistPageView.as_view(), name='create-playlist-page'),
    path('playlists/create-final/', CreatePlaylistFinalView.as_view(), name='create-playlist-final'),
    path('playlists/<playlist_id>/', PlaylistDetailView.as_view(), name='playlist-detail'),
    
    
    path('playlists/public/', PublicPlaylistsView.as_view(), name='public_playlists'),
    path('playlists/public/<int:playlist_id>/', views.public_playlist_detail_simple, name='public_playlist_detail'),
    path('playlists/public/<int:playlist_id>/detail/', views.public_playlist_detail, name='public-playlist-detail'),
    path('playlists/<int:playlist_id>/toggle-public/', views.toggle_playlist_public, name='toggle_playlist_public'),
    
    
    path('playlists/<int:playlist_id>/delete/', DeletePlaylistView.as_view(), name='delete-playlist'),
    path('playlists/<int:playlist_id>/remove-song/', RemoveSongFromPlaylistView.as_view(), name='remove-song-from-playlist'),
    
    
    path('playlists/test-public/', views.test_public_playlists, name='test_public_playlists'),
    
    
    path('account/delete/', DeleteAccountView.as_view(), name='delete-account'),
]
    



