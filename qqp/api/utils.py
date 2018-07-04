"""
Author: Francisco Vaquero <f.vaquero@opianalytics.com>
Enterprise: OPI Analytics

Resources are defined in base
of REST Standard: 

Functions and auxiliar methods
"""
import falcon


def json_error_serializer(request, response, exception):
    json_exception = exception.to_json()
    response.body = json_exception
    response.content_type = falcon.MEDIA_JSON
    response.append_header('Vary', 'Accept')