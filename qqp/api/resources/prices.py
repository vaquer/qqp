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
from datetime import datetime
from sqlalchemy import desc, extract
from sqlalchemy_pagination import paginate
from sqlalchemy.exc import DataError
from db.models import Price


class PricesResource:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('qqpApi.' + __name__)
        self.db = kwargs.get('db_session', NotImplemented)

    def on_get(self, request, response, id_product=None):
        limit = request.get_param_as_int('limit', min=50, max=200) or 100
        page = request.get_param_as_int('page', 1)
        sort = request.get_param('sort', default='fecha_actualizacion', required=False)
        year_observation = request.get_param('anio_observacion', default=datetime.now().year, required=False)
        month_observation = request.get_param('mes_observacion', default=datetime.now().month, required=False)
        cp = request.get_param('cp', default=None, required=False)
        response.content_type = falcon.MEDIA_JSON

        filters = []
        if type(year_observation) is int or type(month_observation) is int:
            month_format = '{:0>2d}'.format(month_observation)
            date_filter = datetime.strptime('{0}{1}'.format(str(year_observation), month_format), '%Y%m')
            filters.append(extract('year', Price.fecha_observacion) == date_filter.year)
            filters.append(extract('month', Price.fecha_observacion) == date_filter.month)

        if cp:
            print("CP")
            filters.append(Price.codigo_postal == cp)

        if id_product:
            filters.append(Price.id_producto == str(id_product))
            try:
                products = self.db.query(Price)\
                    .filter(*filters)\
                    .order_by(desc(Price.fecha_actualizacion))

                if not products:
                    response.status = falcon.HTTP_200
                    response.media = {'error': 'Not Found'}
                    return

            except DataError as data_error:
                self.logger.info('Product not Found {}'.format(id_product))
                response.media = {'error': 'Not Found'}
                response.status = falcon.HTTP_404
                return
        else:
            products = self.db.query(Price)\
                .filter(*filters)\
                .order_by(desc(Price.fecha_actualizacion))\
                .order_by(Price.id_producto)

        print(products)
        page_object = paginate(products, page, limit)
        response.status = falcon.HTTP_200

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
            'fecha_actualizacion': product.fecha_actualizacion.strftime('%d/%m/%Y'),
            'precio': "{0:.2f}".format(product.precio)
        }