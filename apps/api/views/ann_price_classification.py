from rest_framework.generics import ListAPIView

from apps.api.serializers import AnnPriceClassificationSerializer
from apps.api.paginations import StandardResultsSetPagination

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from apps.api.helpers import filter_queryset_by_timestamp  # , queryset_for_list_with_resample_period


#  model: AnnPriceClassification
class ListAnnPriceClassification(ListAPIView):
    """Return AnnPriceClassification.

    /api/v2/ann-price-classification/

    URL query parameters:

    For filtering:

        predicted_ahead_for
        ann_model_id

        transaction_currency -- string BTC, ETH etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, 60=short period
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination:

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    pagination_class = StandardResultsSetPagination
    serializer_class = AnnPriceClassificationSerializer
    filter_fields = (
    'source', 'resample_period', 'counter_currency', 'transaction_currency', 'predicted_ahead_for', 'ann_model_id')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset
