from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from django.contrib import admin
from django.urls import path, include
from .views import ReactAppView
from transcripts import views

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('', ReactAppView.as_view(), name='home'),
]

api_docs = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/documentation/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
urlpatterns += api_docs

urlpatterns += [
    path('api/transcripts/<str:session_id>', views.get_transcripts, name='get_transcripts'),
    path('api/scores/<int:interview_id>/', views.get_interview_scores, name='get_interview_scores'),
]