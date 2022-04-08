from django.urls import path, include
# from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    accounts_views,
    posts_views,
    roadmaps_views
)
app_name = 'apiv1'

router = DefaultRouter()
router.register('profile', accounts_views.ProfileViewSet)
router.register('post', posts_views.GetPostView)
router.register('post', posts_views.GetPostListView)
router.register('create_update_delete_post',
                posts_views.CreateUpdateDeletePostView)
router.register('comment', posts_views.CommentViewSet)
router.register('roadmap', roadmaps_views.RoadMapViewSet)
router.register('step', roadmaps_views.StepViewSet)
router.register('lookback', roadmaps_views.LookBackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # register, login)
    path('register/', accounts_views.RegisterAPIView.as_view(), name="register"),
    path('email-verify/', accounts_views.VerifyEmail.as_view(), name="email-verify"),
    path('login/', accounts_views.LoginAPIView.as_view(), name="login"),
    path('refresh/', accounts_views.RefreshAPIView.as_view(), name='refresh-token'),
    path('logout/', accounts_views.LogoutAPIView.as_view(), name='logout'),
    path('forgot/', accounts_views.ForgotAPIView.as_view(), name='forgot-password'),
    path('reset-password/', accounts_views.ResetAPIView.as_view(),
         name='reset-password'),
    path('delete-account/<uuid:pk>/',
         accounts_views.DeleteUserAPIView.as_view(), name="delete-user"),
    # profile
    path('myprofile/', accounts_views.MyProfileListView.as_view(), name='myprofile'),
    path('following/<uuid:id>/',
         accounts_views.get_following, name='get-following-profile'),
    path('followers/<uuid:id>/', accounts_views.get_followers,
         name='get-followers-profile'),
    path('follow/<uuid:id>/', accounts_views.follow_user, name="follow-user"),
    # post
    path('post/share/<uuid:post_id>', posts_views.share_post, name='post-share'),
    path('post/unshare/<uuid:post_id>',
         posts_views.unshare_post, name='post-unshare'),
    path('post/user/<uuid:id>/', posts_views.post_user, name='post-user'),
    path('followuser/post/', posts_views.GetFollowUserPost.as_view(),
         name='post-follow'),
    path('post/favorite/<uuid:id>/',
         posts_views.get_favorite_post, name="favorite-post"),
    path('post/like/<uuid:id>/', posts_views.like_post, name="like-post"),
    path('post/<uuid:id>/likes/', posts_views.get_profiles_like_post,
         name='get-profiles-like-post'),
    path('post/search/<str:id>/', posts_views.post_search, name="search-post"),
    path('post/hashtag/<uuid:id>/', posts_views.post_hashtag, name="post-hashtag"),
    path('post/<uuid:id>/comment/', posts_views.comments, name="post-comments"),
    # roadmap
    path('roadmap/user/<uuid:id>/',
         roadmaps_views.roadmap_user, name='roadmap-user'),
    path('followuser/roadmap/', roadmaps_views.GetFollowUserRoadmap.as_view(),
         name="roadmap-follow"),
    path('roadmap/search/<str:id>/',
         roadmaps_views.roadmap_search, name="search-roadmap"),
    path('step/roadmap/<uuid:id>/', roadmaps_views.steps, name='step-roadmap'),
    path('step/change-order', roadmaps_views.change_step_order,
         name='change-step-order'),
    path('lookback/step/<uuid:id>/', roadmaps_views.lookbacks, name='lookback-step')
]
