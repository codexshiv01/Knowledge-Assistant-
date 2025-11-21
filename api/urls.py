from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('ask-question/', views.ask_question, name='ask-question'),
    path('queries/', views.query_history, name='query-history'),
    path('stats/', views.system_stats, name='system-stats'),
]
