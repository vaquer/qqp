import falcon
from resources.prices import PricesResource
from resources.products import ProductsResource


api = application = falcon.API()

prices = PricesResource()
products = ProductsResource()

api.add_route('/prices', prices)
api.add_route('/prices/{id_product:int}', prices)
api.add_route('/products', products)
api.add_route('/products/{id_product:int}', products)