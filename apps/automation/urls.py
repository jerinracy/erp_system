from django.urls import path

from .views import (
    RuleCreateView,
    RuleDeleteView,
    RuleListView,
    RuleUpdateView,
)

urlpatterns = [
    path("rules/", RuleListView.as_view()),
    path("rules/create/", RuleCreateView.as_view()),
    path("rules/<int:pk>/", RuleUpdateView.as_view()),
    path("rules/<int:pk>/delete/", RuleDeleteView.as_view()),
]
