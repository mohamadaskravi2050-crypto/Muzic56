from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Music, Playlist, PlaylistSong


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات پروفایل', {'fields': ('profile_image',)}),
    )


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'uploaded_by', 'uploaded_at', 'like_count']
    list_filter = ['uploaded_at', 'artist']
    search_fields = ['title', 'artist', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'like_count']
    date_hierarchy = 'uploaded_at'
    
    def like_count(self, obj):
        return obj.like_count()
    like_count.short_description = 'تعداد لایک'


class PlaylistSongInline(admin.TabularInline):
    model = PlaylistSong
    extra = 1
    raw_id_fields = ['song']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at', 'is_public', 'song_count']
    list_filter = ['is_public', 'created_at', 'owner']
    search_fields = ['name', 'owner__username', 'description']
    readonly_fields = ['created_at']
    inlines = [PlaylistSongInline]
    date_hierarchy = 'created_at'
    
    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = 'تعداد آهنگ'


@admin.register(PlaylistSong)
class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'song', 'added_at']
    list_filter = ['added_at', 'playlist']
    search_fields = ['playlist__name', 'song__title']
    readonly_fields = ['added_at']
    date_hierarchy = 'added_at'

