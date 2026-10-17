from feretui.ext.django import get_urlpatterns_for_feretui_client

from .feret import myferet
from .views import MySession

urlpatterns = get_urlpatterns_for_feretui_client(myferet, session_cls=MySession)
