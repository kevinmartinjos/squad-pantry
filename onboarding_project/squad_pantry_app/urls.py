from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from squad_pantry_app.views import OrderViewSet

order_list = OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
order_detail = OrderViewSet.as_view({
    'get': 'retrieve',
})
cancel_order = OrderViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})

urlpatterns = [
    url(r'^orders/$', order_list, name='order-list'),
    url(r'^orders/(?P<pk>[0-9]+)/$', order_detail, name='order-detail'),
    url(r'^orders/(?P<pk>[0-9]+)/cancel-order$', cancel_order, name='cancel-order'),
]
