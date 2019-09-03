from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('confirm-registration/<slug:username>/<slug:token>',
        views.confirm_action, name='confirm'),
    path('matchmaking', views.matchmaking_action, name='matchmaking'),
    path('matchmaking_refresh', views.matchmaking_refresh_action, name='matchmaking_refresh'),
    path('room/<int:board_id>', views.room_action, name='room'),
    path('room_refresh', views.room_refresh_action, name='room_refresh'),
    path('profile_me', views.profile_me_action, name='profile_me'),
    path('photo/<int:profile_id>', views.get_photo, name='photo'),
    path('initiate/<int:boardid>', views.InitiateBoard, name='home'),
    path('playchess', views.OnlineFiveinaRow, name='playchess'),
    path('endofgame',views.endofgame,name='endofgame'),
    path('refreshboard',views.refresh_board,name='refreshboard'),
    path('rebuildgame/<int:id>',views.rebuild_game,name='rebuildgame'),
]