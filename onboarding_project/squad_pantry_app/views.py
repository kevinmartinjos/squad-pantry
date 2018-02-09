from django.shortcuts import render
from django.views import View
from squad_pantry_app.models import Order, OrderDishRelation, PerformanceMetrics
from squad_pantry_app.serializer import OrderSerializer
from squad_pantry_app.permissions import IsUserWhoPlacedOrder
from rest_framework import permissions, viewsets


class OrderViewSet(viewsets.ModelViewSet):
    """
    Create Order, Cancel Order
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUserWhoPlacedOrder)

    def get_queryset(self):
        return Order.objects.filter(placed_by=self.request.user)


class MetricView(View):
    template_name = 'admin/metrics.html'

    def get(self, request):
        if len(request.GET) > 0:
            if request.GET['end_date'] <= request.GET['start_date']:
                error = 'End Date should be more recent than Start Date'
                return render(request, self.template_name, {'error': error})
            throughput, turnaround_time = PerformanceMetrics.get_metrics_data(request.GET['start_date'],
                                                                              request.GET['end_date'])
            print(throughput, turnaround_time)
            if throughput == 0:
                error = "No Records Found"
                return render(request, self.template_name, {'error': error})
            else:
                return render(request, self.template_name, {'throughput': throughput,
                                                            'turnaround_time': turnaround_time,
                                                            'start': request.GET['start_date'],
                                                            'end': request.GET['end_date']})
        return render(request, self.template_name)
