from django.urls import path
from . import views

urlpatterns = [
    path("monitors/", views.MonitorListCreateView.as_view(), name="monitor-list-create"),
    path("monitors/<str:pk>/", views.MonitorDetailView.as_view()),
    path("monitors/<str:pk>/heartbeat/", views.HeartbeatView.as_view(), name="monitor-heartbeat"),
    path("monitors/<str:pk>/pause/", views.PauseView.as_view(), name="monitor-pause"),     
]