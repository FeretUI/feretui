from feretui.ext.django import get_urlpatterns_for_feretui_client

from .feret import myferet

urlpatterns = get_urlpatterns_for_feretui_client(myferet)
