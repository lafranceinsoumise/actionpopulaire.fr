from rangefilter.filters import NumericRangeFilter


class PriceRangeListFilter(NumericRangeFilter):
    def _make_query_filter(self, _request, validated_data):
        query_params = super()._make_query_filter(_request, validated_data)
        query_params = {
            key: value * 100 for key, value in query_params.items() if value is not None
        }
        return query_params
