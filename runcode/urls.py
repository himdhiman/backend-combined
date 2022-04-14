from django.urls import path
from runcode import views

urlpatterns = [
    path("compilecode/", views.CompileCode.as_view()),
    path("runtests/", views.RunTests.as_view()),
    path("runcode/", views.RunCode.as_view()),
]
