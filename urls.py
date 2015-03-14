from django.conf.urls import patterns, include, url
from django.views.generic import FormView
from views import upload, AllView
from forms import UploadModelFileForm

namespace = 'apksign'
urlpatterns = patterns('',
#     url(r'^$', views.index, name='index'),
    url(r'^$', upload, name='upload'),
    url(r'^all', AllView.as_view(), name='all'), 
    url(r'^progressbarupload/', include('progressbarupload.urls')),
)
