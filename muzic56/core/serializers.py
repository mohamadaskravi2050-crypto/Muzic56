from rest_framework import serializers
from .models import Music, Playlist, PlaylistSong
from django.db.models import Count  

class MusicSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    like_count = serializers.SerializerMethodField()  
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Music
        fields = ['id', 'title', 'artist', 'audio_file', 'audio_url', 'cover_image', 'cover_url', 
                 'uploaded_by', 'uploaded_by_username', 'uploaded_at', 'like_count', 'is_liked']

    def get_audio_url(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_like_count(self, obj):
        
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class PlaylistSerializer(serializers.ModelSerializer):
    song_count = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    cover_url = serializers.SerializerMethodField()
    is_liked_playlist = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'description', 'created_at', 'song_count', 'is_public', 'owner_username', 'cover_url', 'is_liked_playlist']
    
    def get_song_count(self, obj):
        return obj.songs.count()

    def get_cover_url(self, obj):
        request = self.context.get('request')
        first_song = obj.songs.first()
        if first_song and first_song.cover_image:
            return request.build_absolute_uri(first_song.cover_image.url) if request else first_song.cover_image.url
        return None

    def get_is_liked_playlist(self, obj):
        return False

class PlaylistDetailSerializer(serializers.ModelSerializer):
    songs = MusicSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    song_count = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'description', 'songs', 'created_at', 'owner_username', 'is_public', 'song_count']

    def get_song_count(self, obj):

     
        return obj.songs.count()
