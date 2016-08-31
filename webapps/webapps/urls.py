from django.conf.urls import include, url
from hitchhiker import views
from hitchhiker import views as private_views

# import hitchhiker.url
urlpatterns = [
    # Examples:
    # url(r'^$', 'webapps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', private_views.home),
    url(r'^', include('hitchhiker.urls')),
]
