from django.urls import path, re_path
from .views import UserPostsListView, PostCreateView, LikeToggleView, CommentListCreateView, ViewListCreateAPIView, RecommendedPostsView, PostUpdateDeleteView


urlpatterns = [
    re_path(r'^recommended/?$', RecommendedPostsView.as_view(), name='post-list'),
    re_path(r'^add/?$', PostCreateView.as_view(), name='post-create'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/?$', PostUpdateDeleteView.as_view(), name='post-detail-update-delete'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/like/?$', LikeToggleView.as_view(), name='post-like'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/view/?$', ViewListCreateAPIView.as_view(), name='post-view'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/comments/?$', CommentListCreateView.as_view(), name='post-comment'),
    
]
