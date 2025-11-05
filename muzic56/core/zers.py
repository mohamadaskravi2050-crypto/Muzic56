from rest_framework import serializers
from .models import Music

class MusicSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = Music
        fields = ['id', 'title', 'artist', 'audio_file', 'audio_url', 'uploaded_by', 'uploaded_by_username', 'uploaded_at']

    def get_audio_url(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None