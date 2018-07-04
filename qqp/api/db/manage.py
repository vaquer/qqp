"""
Author: Francisco Vaquero <f.vaquero@opianalytics.com>
Enterprise: OPI Analytics

Administrative databse operations
"""


def migrate(engine):
    """
    Create tables on data base
    needed for qqp API
    """
    from qqp.api.db.models import Product, Price, Base
    print("Aplicando migracion de base de datos")
    Base.metadata.create_all(engine)


def create_qqp_engine():
    """
    Create an instance of the
    database engine. This function 
    must be called only once by 
    the qqp instance API
    """
    from sqlalchemy import create_engine
    from qqp import settings
    engine = create_engine('postgresql+psycopg2://{username}:{password}@{host}:{port}/qqp'.format(**settings.DATABASE['qqp']))
    return engine
