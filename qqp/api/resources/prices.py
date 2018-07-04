"""
Author: Francisco Vaquero <f.vaquero@opianalytics.com>
Enterprise: OPI Analytics

Resources are defined in base
of REST Standard: 

Definition of Price Resource
"""
import json
import falcon
import logging
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from qqp.api.db.models import Price


class PricesResource:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('qqpApi.' + __name__)
        self.db = kwargs.get('db_session', NotImplemented)

    def on_get(self, request, response, id_product=None):
        limit = request.get_param_as_int('limit', min=50, max=200) or 100
        page = request.get_param_as_int('page', 1)

        if id_product:
            products = self.db.query(Price)\
                .filter(Price.id_producto == str(id_product))\
                .yield_per(limit)
        else:
            products = self.db.query(Price)\
                .order_by(desc(Price.fecha_actualizacion))\
                .order_by(Price.id_producto)

        page_object = paginate(products, page, limit)
        response.status = falcon.HTTP_200
        response.content_type = falcon.MEDIA_JSON
        response.media = {
            'results': [self.convert_to_dict(product) for product in page_object.items],
            'meta': {
                'page': page,
                'limit': limit,
                'total': page_object.total,
                'pages': page_object.pages
            }
        }

    def convert_to_dict(self, product):
        return {
            'id_producto': product.id_producto,
            'id_marca': product.id_marca,
            'id_establecimiento': product.id_establecimiento,
            'marca': product.marca,
            'establecimiento': product.establecimiento,
            'estado': product.estado,
            'direccion': product.direccion,
            'cp': product.codigo_postal,
            'fecha_observacion': product.fecha_observacion.strftime('%d/%m/%Y'),
            'fecha_actualizacion': product.fecha_actualizacion.strftime('%d/%m/%Y')
        }