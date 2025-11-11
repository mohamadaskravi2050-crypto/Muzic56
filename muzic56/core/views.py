
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Max
from rest_framework.permissions import AllowAny
from .models import Music, Playlist, PlaylistSong
from .serializers import MusicSerializer, PlaylistSerializer


User = get_user_model()



class RegisterView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username or not password:
                return Response(
                    {"error": "Username and password required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(username=username).exists():
                return Response(
                    {"error": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.create_user(username=username, password=password)

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User created successfully",
                    "access": str(refresh.access_token),
                    "username": user.username,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username or not password:
                return Response(
                    {"error": "Username and password required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = authenticate(username=username, password=password)
            if user is None:
                return Response(
                    {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {"access": str(refresh.access_token), "username": user.username}
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Successfully logged out"})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile_image_url = None
            if user.profile_image:
                profile_image_url = request.build_absolute_uri(user.profile_image.url)

            return Response(
                {"username": user.username, "profile_image": profile_image_url}
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class MusicUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            title = request.data.get("title")
            artist = request.data.get("artist", "")
            audio_file = request.FILES.get("audio_file")
            cover_image = request.FILES.get("cover_image")

            if not title or not audio_file:
                return Response(
                    {"error": "Title and audio file are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            allowed_formats = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/x-m4a"]
            if audio_file.content_type not in allowed_formats:
                return Response(
                    {"error": "Invalid audio format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            music = Music.objects.create(
                title=title,
                artist=artist,
                audio_file=audio_file,
                cover_image=cover_image,
                uploaded_by=request.user,
            )

            return Response(
                {
                    "message": "Music uploaded successfully",
                    "music": {
                        "id": music.id,
                        "title": music.title,
                        "artist": music.artist,
                        "audio_url": request.build_absolute_uri(music.audio_file.url),
                        "cover_url": (
                            request.build_absolute_uri(music.cover_image.url)
                            if music.cover_image
                            else None
                        ),
                    },
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MusicListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            music_list = Music.objects.all().order_by("-uploaded_at")
            serializer = MusicSerializer(
                music_list, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LikeMusicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, music_id):
        try:
            music = Music.objects.get(id=music_id)
            if music.likes.filter(id=request.user.id).exists():
                music.likes.remove(request.user)
                liked = False
            else:
                music.likes.add(request.user)
                liked = True

            return Response({"liked": liked, "like_count": music.like_count()})
        except Music.DoesNotExist:
            return Response(
                {"error": "Music not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LikedMusicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            liked_music = Music.objects.filter(likes=request.user)
            serializer = MusicSerializer(
                liked_music, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class PlaylistListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_playlists = Playlist.objects.filter(owner=request.user)
            playlist_data = PlaylistSerializer(user_playlists, many=True).data

            liked_songs_count = Music.objects.filter(likes=request.user).count()
            liked_playlist = {
                "id": "liked_songs",
                "name": "Liked Songs",
                "song_count": liked_songs_count,
                "is_liked_playlist": True,
                "is_public": False,
            }

            return Response([liked_playlist] + playlist_data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreatePlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name = request.data.get("name")
            description = request.data.get("description", "")
            is_public = request.data.get("is_public", False)

            if not name:
                return Response(
                    {"error": "Playlist name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            playlist = Playlist.objects.create(
                name=name,
                description=description,
                owner=request.user,
                is_public=is_public,
            )
            return Response(
                {
                    "id": playlist.id,
                    "name": playlist.name,
                    "is_public": playlist.is_public,
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddToPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            playlist_id = request.data.get("playlist_id")
            song_id = request.data.get("song_id")

            if playlist_id == "liked_songs":
                song = Music.objects.get(id=song_id)
                if not song.likes.filter(id=request.user.id).exists():
                    song.likes.add(request.user)
                    return Response({"message": "Added to liked songs"})
                else:
                    return Response({"message": "Already in liked songs"})
            else:
                playlist = Playlist.objects.get(id=playlist_id, owner=request.user)
                song = Music.objects.get(id=song_id)

                if not PlaylistSong.objects.filter(
                    playlist=playlist, song=song
                ).exists():
                    PlaylistSong.objects.create(playlist=playlist, song=song)
                    return Response({"message": "Song added to playlist"})
                else:
                    return Response({"message": "Song already in playlist"})

        except (Playlist.DoesNotExist, Music.DoesNotExist):
            return Response(
                {"error": "Playlist or song not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUserPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            playlists = Playlist.objects.filter(owner=request.user)
            return Response(PlaylistSerializer(playlists, many=True).data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreatePlaylistPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            all_music = Music.objects.all()
            serializer = MusicSerializer(
                all_music, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreatePlaylistFinalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name = request.data.get("name")
            description = request.data.get("description", "")
            song_ids = request.data.get("song_ids", [])
            is_public = request.data.get("is_public", True)

            if not name:
                return Response(
                    {"error": "Playlist name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            playlist = Playlist.objects.create(
                name=name,
                description=description,
                owner=request.user,
                is_public=is_public,
            )

            for song_id in song_ids:
                try:
                    song = Music.objects.get(id=song_id)
                    PlaylistSong.objects.create(playlist=playlist, song=song)
                except Music.DoesNotExist:
                    continue

            return Response(
                {
                    "message": "Playlist created successfully",
                    "playlist_id": playlist.id,
                    "song_count": len(song_ids),
                    "is_public": playlist.is_public,
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlaylistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, playlist_id):
        try:
            if playlist_id == "liked_songs":
                liked_songs = Music.objects.filter(likes=request.user)
                playlist_data = {
                    "id": "liked_songs",
                    "name": "Liked Songs",
                    "description": "Your liked songs",
                    "is_public": False,
                    "owner_username": request.user.username,
                    "songs": MusicSerializer(
                        liked_songs, many=True, context={"request": request}
                    ).data,
                }
            else:
                playlist = Playlist.objects.get(id=int(playlist_id), owner=request.user)
                playlist_songs = PlaylistSong.objects.filter(
                    playlist=playlist
                ).order_by("added_at")
                songs = [ps.song for ps in playlist_songs]

                playlist_data = {
                    "id": playlist.id,
                    "name": playlist.name,
                    "description": playlist.description,
                    "is_public": playlist.is_public,
                    "owner_username": playlist.owner.username,
                    "songs": MusicSerializer(
                        songs, many=True, context={"request": request}
                    ).data,
                }

            return Response(playlist_data)

        except Playlist.DoesNotExist:
            return Response(
                {"error": "Playlist not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeletePlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, playlist_id):
        try:
            playlist = Playlist.objects.get(id=playlist_id, owner=request.user)
            playlist.delete()
            return Response({"message": "Playlist deleted successfully"})
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found"}, status=404)


class RemoveSongFromPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, playlist_id):
        try:
            song_id = request.data.get("song_id")
            playlist = Playlist.objects.get(id=playlist_id, owner=request.user)
            song = Music.objects.get(id=song_id)

            PlaylistSong.objects.filter(playlist=playlist, song=song).delete()

            return Response({"message": "Song removed from playlist"})
        except (Playlist.DoesNotExist, Music.DoesNotExist):
            return Response({"error": "Playlist or song not found"}, status=404)


class PublicPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            print("🔍 Fetching public playlists...")

            
            playlists = Playlist.objects.filter(is_public=True)
            print(f"📊 Found {playlists.count()} public playlists")

            playlists_data = []
            for playlist in playlists:
                
                playlist_info = {
                    "id": playlist.id,
                    "name": playlist.name or "Unnamed Playlist",
                    "owner_name": (
                        playlist.owner.username if playlist.owner else "Unknown"
                    ),
                    "description": playlist.description or "",
                    "song_count": 0,
                    "cover_url": None,
                }

                
                try:
                    playlist_info["song_count"] = PlaylistSong.objects.filter(
                        playlist=playlist
                    ).count()
                except Exception as e:
                    print(f"⚠️ Error counting songs for playlist {playlist.id}: {e}")
                    playlist_info["song_count"] = 0

                
                try:
                    first_song_rel = PlaylistSong.objects.filter(
                        playlist=playlist
                    ).first()
                    if (
                        first_song_rel
                        and first_song_rel.song
                        and first_song_rel.song.cover_image
                    ):
                        playlist_info["cover_url"] = request.build_absolute_uri(
                            first_song_rel.song.cover_image.url
                        )
                except Exception as e:
                    print(f"⚠️ Error getting cover for playlist {playlist.id}: {e}")

                playlists_data.append(playlist_info)
                print(f"✅ Added playlist: {playlist_info['name']}")

            print(f"🎉 Successfully processed {len(playlists_data)} playlists")
            return Response(playlists_data)

        except Exception as e:
            print(f"❌ Critical error in PublicPlaylistsView: {str(e)}")
            import traceback

            print(f"❌ Traceback: {traceback.format_exc()}")
            return Response(
                {"error": "Failed to load public playlists", "debug": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def public_playlist_detail_simple(request, playlist_id):
    try:
        print(f"🔍 Loading public playlist detail: {playlist_id}")

        playlist = Playlist.objects.get(id=playlist_id, is_public=True)

        songs_data = []
        try:
            playlist_songs = PlaylistSong.objects.filter(
                playlist=playlist
            ).select_related("song")

            for playlist_song in playlist_songs:
                song = playlist_song.song
                song_data = {
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist or "Unknown Artist",
                    "uploaded_by": song.uploaded_by.username,
                }

                
                try:
                    song_data["audio_url"] = request.build_absolute_uri(
                        song.audio_file.url
                    )
                except:
                    song_data["audio_url"] = None

                try:
                    if song.cover_image:
                        song_data["cover_url"] = request.build_absolute_uri(
                            song.cover_image.url
                        )
                    else:
                        song_data["cover_url"] = None
                except:
                    song_data["cover_url"] = None

                songs_data.append(song_data)
        except Exception as e:
            print(f"⚠️ Error loading songs: {e}")

        playlist_data = {
            "id": playlist.id,
            "name": playlist.name,
            "owner": playlist.owner.username,
            "description": playlist.description or "No description",
            "song_count": len(songs_data),
            "songs": songs_data,
        }

        return JsonResponse(playlist_data)

    except Playlist.DoesNotExist:
        return JsonResponse({"error": "Playlist not found or not public"}, status=404)
    except Exception as e:
        print(f"❌ Error in public_playlist_detail_simple: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
def toggle_playlist_public(request, playlist_id):
    try:
        playlist = Playlist.objects.get(id=playlist_id, owner=request.user)
        playlist.is_public = not playlist.is_public
        playlist.save()

        return JsonResponse(
            {
                "message": f'Playlist is now {"public" if playlist.is_public else "private"}',
                "is_public": playlist.is_public,
            }
        )
    except Playlist.DoesNotExist:
        return JsonResponse({"error": "Playlist not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def test_public_playlists(request):
    """Endpoint تست برای دیباگ"""
    try:
        print("🧪 Testing public playlists endpoint...")
        print(f"👤 Authenticated user: {request.user.username}")

        
        playlists_count = Playlist.objects.filter(is_public=True).count()

        return JsonResponse(
            {
                "message": "Test successful",
                "user": request.user.username,
                "public_playlists_count": playlists_count,
                "status": "working",
            }
        )

    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback

        print(f"❌ Traceback: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)


from django.db.models import Count, Q


class PopularMusicView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """لیست 5 موزیک پرطرفدار بر اساس تعداد لایک"""
        try:
            print("🔥 Fetching popular music...")

            # روش بهینه: استفاده از annotate برای شمارش لایک‌ها
            from django.db.models import Count

            popular_music = Music.objects.annotate(
                likes_count=Count("likes")  # نام فیلد را به likes_count تغییر دادیم
            ).order_by("-likes_count")[:5]

            print(f"✅ Found {popular_music.count()} popular songs")

            # دیباگ: چک کردن داده‌ها
            for music in popular_music:
                print(f"🎵 {music.title}: {music.likes_count} likes")

            serializer = MusicSerializer(
                popular_music, many=True, context={"request": request}
            )
            return Response(serializer.data)

        except Exception as e:
            print(f"❌ Error in PopularMusicView: {str(e)}")
            import traceback

            print(f"❌ Traceback: {traceback.format_exc()}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchMusicView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """جستجوی موزیک"""
        try:
            query = request.GET.get("q", "").strip()

            if not query:
                return Response([])

            # جستجو در دیتابیس
            results = Music.objects.filter(
                Q(title__icontains=query) | Q(artist__icontains=query)
            ).order_by("-uploaded_at")[:10]

            serializer = MusicSerializer(
                results, many=True, context={"request": request}
            )
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from django.contrib.auth import get_user_model

User = get_user_model()


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            print(f"🗑️ Starting account deletion for user: {user.username}")

            # 1. ذخیره اطلاعات برای لاگ
            username = user.username
            user_id = user.id

            # 2. حذف تمام موزیک‌های کاربر
            user_music = Music.objects.filter(uploaded_by=user)
            music_count = user_music.count()
            user_music.delete()
            print(f"🎵 Deleted {music_count} music files")

            # 3. حذف تمام پلی‌لیست‌های کاربر
            user_playlists = Playlist.objects.filter(owner=user)
            playlist_count = user_playlists.count()
            user_playlists.delete()
            print(f"📋 Deleted {playlist_count} playlists")

            # 4. حذف لایک‌های کاربر
            liked_music_count = user.liked_music.count()
            user.liked_music.clear()
            print(f"❤️ Removed {liked_music_count} likes")

            # 5. حذف خود کاربر از دیتابیس
            user.delete()

            print(f"✅ Account {username} (ID: {user_id}) deleted successfully")

            return Response(
                {
                    "success": True,
                    "message": "Account and all associated data deleted successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Error deleting account: {str(e)}")
            import traceback

            print(f"❌ Traceback: {traceback.format_exc()}")
            return Response(
                {"success": False, "error": f"Error deleting account: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            print(f"🗑️ Starting account deletion for user: {user.username}")

            # 1. ذخیره اطلاعات برای لاگ
            username = user.username
            user_id = user.id

            # 2. حذف تمام موزیک‌های کاربر
            user_music = Music.objects.filter(uploaded_by=user)
            music_count = user_music.count()
            user_music.delete()
            print(f"🎵 Deleted {music_count} music files")

            # 3. حذف تمام پلی‌لیست‌های کاربر
            user_playlists = Playlist.objects.filter(owner=user)
            playlist_count = user_playlists.count()
            user_playlists.delete()
            print(f"📋 Deleted {playlist_count} playlists")

            # 4. حذف لایک‌های کاربر
            liked_music_count = user.liked_music.count()
            user.liked_music.clear()
            print(f"❤️ Removed {liked_music_count} likes")

            # 5. حذف خود کاربر از دیتابیس
            user.delete()

            print(f"✅ Account {username} (ID: {user_id}) deleted successfully")

            return Response(
                {
                    "success": True,
                    "message": "Account and all associated data deleted successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Error deleting account: {str(e)}")
            return Response(
                {"success": False, "error": f"Error deleting account: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteMusicView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, music_id):
        try:
            music = Music.objects.get(id=music_id, uploaded_by=request.user)
            music.delete()

            return Response(
                {"success": True, "message": "Music deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Music.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": "Music not found or you do not have permission to delete it",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": f"Error deleting music: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def public_playlist_detail(request, playlist_id):
    try:
        print(f"🔍 Loading public playlist detail: {playlist_id}")

        
        playlist = Playlist.objects.get(id=playlist_id, is_public=True)

       
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist).select_related(
            "song"
        )
        songs_data = []

        for playlist_song in playlist_songs:
            song = playlist_song.song
            song_data = {
                "id": song.id,
                "title": song.title,
                "artist": song.artist or "Unknown Artist",
                "uploaded_by": song.uploaded_by.username,
            }

            
            try:
                if song.audio_file:
                    song_data["audio_url"] = request.build_absolute_uri(
                        song.audio_file.url
                    )
                else:
                    song_data["audio_url"] = None
            except Exception as e:
                print(f"⚠️ Error getting audio URL: {e}")
                song_data["audio_url"] = None

            try:
                if song.cover_image:
                    song_data["cover_url"] = request.build_absolute_uri(
                        song.cover_image.url
                    )
                else:
                    song_data["cover_url"] = None
            except Exception as e:
                print(f"⚠️ Error getting cover URL: {e}")
                song_data["cover_url"] = None

            songs_data.append(song_data)

        playlist_data = {
            "id": playlist.id,
            "name": playlist.name,
            "owner": playlist.owner.username,
            "description": playlist.description or "",
            "song_count": len(songs_data),
            "songs": songs_data,
            "is_public": playlist.is_public,
        }

        print(
            f"✅ Successfully loaded playlist: {playlist.name} with {len(songs_data)} songs"
        )
        return JsonResponse(playlist_data)

    except Playlist.DoesNotExist:
        print(f"❌ Playlist not found or not public: {playlist_id}")
        return JsonResponse({"error": "Playlist not found or not public"}, status=404)
    except Exception as e:
        print(f"❌ Error in public_playlist_detail: {str(e)}")
        import traceback

        print(f"❌ Traceback: {traceback.format_exc()}")
        return JsonResponse({"error": "Internal server error"}, status=500)
