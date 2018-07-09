import os
import falcon
from sqlalchemy.orm import sessionmaker
from resources.prices import PricesResource
from resources.products import ProductsResource
from db.manage import create_qqp_engine, migrate
from utils import json_error_serializer

databse_engine = create_qqp_engine()
Session = sessionmaker(bind=databse_engine, autocommit=True, autoflush=True)
database_session = Session()

if os.environ.get('RUN_MIGRATIONS') == 'True':
    migrate(databse_engine)

api = application = falcon.API(media_type=falcon.MEDIA_JSON)

prices = PricesResource(db_session=database_session)
products = ProductsResource(db_session=database_session)

api.set_error_serializer(json_error_serializer)
api.add_route('/prices', prices)
api.add_route('/prices/{id_product:int}', prices)
api.add_route('/products', products)
api.add_route('/products/{id_product:int}', products)