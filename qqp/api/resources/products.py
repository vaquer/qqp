"""
Author: Francisco Vaquero <f.vaquero@opianalytics.com>
Enterprise: OPI Analytics

Resources are defined in base
of REST Standard: 

Definition of Products Resource
"""

import json
import logging
import falcon
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from sqlalchemy.orm.exc import NoResultFound
from db.models import Product

class ProductsResource:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('qqpApi.' + __name__)
        self.db = kwargs.get('db_session', NotImplemented)

    def on_get(self, request, response, id_product=None):
        if id_product is None:
            limit = request.get_param_as_int('limit', min=50, max=200) or 100
            page = request.get_param_as_int('page', 1)

            products = self.db.query(Product)\
                .order_by(Product.nombre)

            page_object = paginate(products, page, limit)
            response.media = {
                'results': [self.convert_to_dict(product) for product in page_object.items],
                'meta': {
                    'page': page,
                    'limit': limit,
                    'total': page_object.total,
                    'pages': page_object.pages
                }
            }
        else:
            try:
                products = self.db.query(Product)\
                    .filter(Product.id == id_product)\
                    .first()
                if not products:
                    response.status = falcon.HTTP_404
                    return

                response.media = self.convert_to_dict(products)
            except NoResultFound as not_found_error:
                self.logger.info('Product not Found {}'.format(id_product))
                response.status = falcon.HTTP_404
                return
            except Exception as extreme_exception:
                self.logger.error('Exception in Product endpoint id_product: {}, exception: {}'.format(id_product, str(extreme_exception)))
                response.status = falcon.HTTP_500
                return

        response.status = falcon.HTTP_200
        response.content_type = falcon.MEDIA_JSON

    def convert_to_dict(self, product):
        return {
            'id': product.id,
            'id_profeco': product.id_profeco,
            'nombre': product.nombre
        }
