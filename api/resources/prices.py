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


class PricesResource:
    def __init__(self, *kwargs):
        self.logger = logging.getLogger('qqpApi.' + __name__)

    def on_get(self, request, response, id_product=None):
        limit = request.get_param_as_int('limit')
        page = request.get_param_as_int('page')

        response.status = falcon.HTTP_200
        response.content_type = falcon.MEDIA_JSON
        response.media = []
