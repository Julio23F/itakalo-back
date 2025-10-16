import math
import sys
import time
from datetime import datetime

from drf_yasg import openapi
from lib.loguru import logger

DEFAULT_PER_PAGE = 12

class FilterPagination:

    @staticmethod
    def filter_and_pagination(request, model_reference, queries=None,
                              order_by_array=None, special_order_by=None):
        start_time = time.time()

        model_fields = [field.name for field in model_reference._meta.get_fields()]
        filter_params = request.GET
        custom_filter = {}

        # Construction du filtre
        if filter_params:
            for k, v in filter_params.items():
                if k in model_fields:
                    field_type = model_reference._meta.get_field(k).get_internal_type()
                    if field_type in ("ForeignKey", "IntegerField"):
                        custom_filter[k] = v
                    else:
                        custom_filter[f"{k}__icontains"] = v
                else:
                    k_rsplit = k.rsplit('__', 1)
                    if k_rsplit[-1] in ['from', 'to']:
                        field_type = model_reference._meta.get_field(k_rsplit[0]).get_internal_type()
                        if field_type in [
                            "DateField", "DateTimeField", "DecimalField",
                            "FloatField", "IntegerField", "PositiveIntegerField"
                        ]:
                            compare = '__gte' if k_rsplit[-1] == 'from' else '__lte'
                            if field_type == "DateTimeField":
                                v = v + " 00:00:00" if k_rsplit[-1] == 'from' else v + " 23:59:59"
                            custom_filter[f"{k_rsplit[0]}{compare}"] = v
                    elif k_rsplit[-1] == 'array':
                        custom_filter[f"{k_rsplit[0]}__in"] = v
                    elif k_rsplit[-1] == 'exact':
                        custom_filter[f"{k_rsplit[0]}__exact"] = v
                    else:
                        pass

        queryset_filter = model_reference.objects.filter(**custom_filter)
        if queries:
            queryset_filter = queryset_filter.filter(queries)

        # Tri
        order_by_field = filter_params.get('order_by') if (
            'order_by' in filter_params and filter_params['order_by'] in model_fields
        ) else 'id'
        order_type = filter_params.get('order_type', '')
        if order_type != '-':
            order_type = ''
        order_by = order_type + order_by_field

        # Pagination
        per_page = int(filter_params.get('per_page', DEFAULT_PER_PAGE) or DEFAULT_PER_PAGE)
        if per_page == 0:
            per_page = DEFAULT_PER_PAGE
        page_no = int(filter_params.get('page_no', 1) or 1)

        start_limit = (per_page * page_no) - per_page
        end_limit = per_page * page_no

        total_object_count = queryset_filter.count()
        total_pages = math.ceil(total_object_count / per_page)

        # Order
        if order_by_array:
            oba = order_by_array + (order_by,)
            queryset_filter = queryset_filter.order_by(*oba)
        else:
            queryset_filter = queryset_filter.order_by(order_by)

        # special_order_by => pas de slicing
        if special_order_by:
            queryset = queryset_filter.filter(special_order_by['queries'])
            if special_order_by.get('orders'):
                queryset = queryset.order_by(special_order_by['orders'])
        else:
            queryset = queryset_filter[start_limit:end_limit]

        queryset = (
            queryset
            .only("id", "created_at", "updated_at")
        )

        # On fait un list(...) pour la mesure, SANS l'affecter au 'dataset'
        qs_list = list(queryset)
        data_count = len(qs_list)
        data_size_mb = sys.getsizeof(qs_list) / (1024 * 1024)
        elapsed = time.time() - start_time

        logger.debug(
            f"[filter_and_pagination OPTIM] Model={model_reference.__name__}, "
            f"count={data_count}, (~{data_size_mb:.2f} MB) in {elapsed:.3f}s"
        )

        dataset = {
            'queryset': queryset,  
            'pagination': {
                'per_page': per_page,
                'current_page': page_no,
                'total_count': total_object_count,
                'total_pages': total_pages
            }
        }
        return dataset

    @staticmethod
    def get_search_inverse(request, model_reference, serializer_class, search_field='title'):
        """
        Recherche inverse : trouve les objets dont mots_cles_recherches 
        contient la valeur recherchée dans search_field
        
        Args:
            request: requête Django
            model_reference: modèle Django (ex: Product)
            serializer_class: serializer pour les résultats
            search_field: champ sur lequel effectuer la recherche (par défaut 'title')
        
        Returns:
            Liste sérialisée des résultats ou None si pas de recherche
        """
        search_value = request.GET.get(search_field)
        
        if not search_value:
            return None
        
        # Recherche les objets où mots_cles_recherches contient la valeur recherchée
        # __icontains permet une recherche insensible à la casse
        inverse_queryset = model_reference.objects.filter(
            mots_cles_recherches__icontains=search_value.lower()
        ).distinct()
        
        # Sérialise les résultats
        serialized_inverse = serializer_class(inverse_queryset, many=True).data
        
        logger.debug(
            f"[search_inverse] search_field={search_field}, "
            f"search_value={search_value}, found={inverse_queryset.count()} results"
        )
        
        return serialized_inverse

    @staticmethod
    def generate_pagination_params(description=None, additional_params=None):
        """
        Génère les paramètres pour la doc (Swagger).
        """
        if additional_params is None:
            additional_params = []

        per_page_param = openapi.Parameter(
            'per_page',
            openapi.IN_QUERY,
            description="counts per page",
            type=openapi.TYPE_NUMBER
        )
        page_no_param = openapi.Parameter(
            'page_no',
            openapi.IN_QUERY,
            description="page numbers",
            type=openapi.TYPE_NUMBER
        )
        order_by_param = openapi.Parameter(
            'order_by',
            openapi.IN_QUERY,
            description="name of field to sort",
            type=openapi.TYPE_STRING
        )
        order_type_param = openapi.Parameter(
            'order_type',
            openapi.IN_QUERY,
            description="type of field to sort. Must be '-' or ''",
            type=openapi.TYPE_STRING
        )

        desc = "Search keyword. You can input any field name and value"
        if description:
            desc = description

        search_param = openapi.Parameter(
            'keyword',
            openapi.IN_QUERY,
            description=desc,
            type=openapi.TYPE_STRING
        )

        res = [per_page_param, page_no_param, order_by_param, order_type_param, search_param]
        if additional_params:
            res += additional_params
        return res

    @staticmethod
    def get_pagination_data(request, model_class, serializer_class,
                           queries=None, order_by_array=None, special_order_by=None,
                           enable_search_inverse=False, search_inverse_field='title'):
        """
        Retourne data sérialisée + pagination + search_inverse optionnel.
        
        Args:
            enable_search_inverse: active la recherche inverse (défaut: False)
            search_inverse_field: champ sur lequel effectuer la recherche inverse (défaut: 'title')
        """
        queryset_info = FilterPagination.filter_and_pagination(
            request,
            model_class,
            queries,
            order_by_array,
            special_order_by
        )
        
        # Sérialise la partie 'queryset'
        serialized = serializer_class(queryset_info['queryset'], many=True).data
        
        result = {
            'dataset': serialized,
            'pagination': queryset_info['pagination']
        }
        
        # Ajoute search_inverse si activé
        if enable_search_inverse:
            search_inverse_result = FilterPagination.get_search_inverse(
                request, 
                model_class, 
                serializer_class,
                search_inverse_field
            )
            result['search_inverse'] = search_inverse_result
        
        return result