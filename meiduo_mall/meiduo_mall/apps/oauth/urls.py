from django.conf.urls import url
from oauth.views import QQAuthURLView, QQAuthUserView

urlpatterns=[
    url(r'^qq/authorization/$', view=QQAuthURLView.as_view()),
    url(r'^qq/user/$', view=QQAuthUserView.as_view())
]