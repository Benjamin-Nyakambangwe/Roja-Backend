import django_filters
from .models import Property, HouseLocation


class PropertyFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    address = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    deposit_min = django_filters.NumberFilter(field_name='deposit', lookup_expr='gte')
    deposit_max = django_filters.NumberFilter(field_name='deposit', lookup_expr='lte')
    bedrooms_min = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    bathrooms_min = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')
    area_min = django_filters.NumberFilter(field_name='area', lookup_expr='gte')
    area_max = django_filters.NumberFilter(field_name='area', lookup_expr='lte')
    is_available = django_filters.BooleanFilter()
    preferred_lease_term_min = django_filters.NumberFilter(field_name='preferred_lease_term', lookup_expr='gte')
    preferred_lease_term_max = django_filters.NumberFilter(field_name='preferred_lease_term', lookup_expr='lte')
    accepts_pets = django_filters.BooleanFilter()
    pet_deposit_min = django_filters.NumberFilter(field_name='pet_deposit', lookup_expr='gte')
    pet_deposit_max = django_filters.NumberFilter(field_name='pet_deposit', lookup_expr='lte')
    accepts_smokers = django_filters.BooleanFilter()
    pool = django_filters.BooleanFilter()
    garden = django_filters.BooleanFilter()
    type = django_filters.CharFilter(field_name='type__name', lookup_expr= 'icontains')
    location = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains')

    class Meta:
        model = Property
        fields = ['title', 'description', 'address', 'price', 'deposit', 'bedrooms', 'bathrooms', 'area', 
                  'is_available', 'preferred_lease_term', 'accepts_pets', 'pet_deposit', 'accepts_smokers', 
                  'pool', 'garden','type', 'location']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.distinct()