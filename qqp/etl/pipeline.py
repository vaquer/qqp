import luigi
import json
import datetime
from scrapper import Categories, Geography, Products, Brands, Prices


class DownloadProductCategories(luigi.Task):
    """
    Luigi.Task
    Input: output/products-{date}.json
    Output: output/branded-products-{date}.json

    Descarga la lista de categorias de productos
    registradas en la base de datos de QQP
    Estructura:
        - Categorias Principales
            - Sub Categoria A
            - Sub Categoria B
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def run(self):
        scrapper = Categories()
        scrapper.set_main_categories()
        scrapper.set_sub_a_categories()
        scrapper.set_sub_b_categories()

        scrapper.make_json_serializable()

        with self.output().open('w') as json_file:
            json.dump(scrapper.main_categories, json_file)

    def output(self):
        return luigi.LocalTarget('output/categories-{}.json'.format(self.date.strftime('%Y%m%d')))


class DownloadGeograpyProducts(luigi.Task):
    """
    Luigi.Task
    Input: output/products-{date}.json
    Output: output/branded-products-{date}.json

    Descarga la lista zonas geograficas registradas
    en la base de datos de QQP:
    Estructura:
        - Ciudad
            - Municipios
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def run(self):
        scrapper = Geography()
        scrapper.set_states()
        scrapper.set_regions()
        scrapper.make_json_serializable()
        with self.output().open('w') as json_file:
            json.dump(scrapper.cities, json_file)

    def output(self):
        return luigi.LocalTarget('output/geography-{}.json'.format(self.date.strftime('%Y%m%d')))


class DownloadProducts(luigi.Task):
    """
    Luigi.Task
    Input: output/products-{date}.json
    Output: output/branded-products-{date}.json

    Descarga la lista de productos sin marca
    filtrada por zonas geograficas
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def run(self):
        categories_f = yield DownloadProductCategories(date=self.date)
        geography_f = yield DownloadGeograpyProducts(date=self.date)
        products = None
        geography = None

        with categories_f.open('r') as categories_file:
            categories = json.load(categories_file)

        with geography_f.open('r') as geography_file:
            geography = json.load(geography_file)

        scrapper = Products(geopgraphy=geography, categories=categories)
        scrapper.set_products()
        scrapper.make_json_serializable()

        with self.output().open('w') as products_json:
            json.dump(scrapper.products, products_json)

    def output(self):
        return luigi.LocalTarget('output/products-{}.json'.format(self.date.strftime('%Y%m%d')))


class DownloadBrands(luigi.Task):
    """
    Luigi.Task
    Input: output/products-{date}.json
    Output: output/branded-products-{date}.json

    Descarga las marcas por producto y zonas geograficas
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        return DownloadProducts(date=self.date)

    def run(self):

        with self.input().open('r') as products_file:
            products = json.load(products_file)

        with open('output/geography-{}.json'.format(self.date.strftime('%Y%m%d'))) as geo_file:
            geography = json.load(geo_file)

        scrapper = Brands(geography=geography, products=products)
        scrapper.set_brands_by_product()
        scrapper.make_json_serializable()

        with self.output().open('w') as products_file_b:
            json.dump(scrapper.products, products_file_b)

    def output(self):
        return luigi.LocalTarget('output/branded-products-{}.json'.format(self.date.strftime('%Y%m%d')))


class DownloadPrices(luigi.Task):
    """
    Luigi.Task
    Input: output/branded-products-{date}.json
    Output: output/prices-per-product-{}.json

    Descarga los precios de los articulos
    relacionados con marcas y zonas geograficas
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        return DownloadBrands(date=self.date)

    def run(self):
        with self.input().open('r') as branded_product:
            products = json.load(branded_product)

        with open('output/geography-{}.json'.format(self.date.strftime('%Y%m%d'))) as geo_file:
            geography = json.load(geo_file)

        prices_scrapper = Prices(products=products, geography=geography, date=self.date)
        prices_scrapper.get_prices_per_product()

        with self.output().open('w') as prices_file:
            json.dump(prices_scrapper.get_prices(), prices_file)

    def output(self):
        return luigi.LocalTarget('output/prices-per-product-{}.json'.format(self.date.strftime('%Y%m%d')))


class InsertProductCatalog(luigi.Task):
    """
    Luigi.Task
    Input: output/branded-products-{date}.json
    Output: output/prices-per-product-{}.json

    Inserta en la base de datos el catalogo
    de productos
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        return DownloadPrices(date=self.date)

    def run(self):
        count = 1
        with open('output/branded-products-{}.json'.format(self.date.strftime('%Y%m%d')),'r') as prices_file:
            from sqlalchemy.orm import sessionmaker
            from qqp.api.db.manage import create_qqp_engine
            from qqp.api.db.models import Product
            from qqp.api.db.manage import migrate

            databse_engine = create_qqp_engine()
            migrate(databse_engine)
            Session = sessionmaker(bind=databse_engine)
            db = Session()

            prices = json.load(prices_file)

            for product in prices:
                instance = db.query(Product).filter_by(
                    nombre=product.get('nombre'),
                    id_profeco=str(product.get('id')),
                    catalogo=product.get('catalogo'),
                    categoria=product.get('categoria'),
                ).first()

                if not instance:
                    new_product = Product(
                        nombre=product.get('nombre').strip(),
                        id_profeco=product.get('id'),
                        catalogo=product.get('catalogo'),
                        categoria=product.get('categoria')
                    )
                    db.add(new_product)
                    db.commit()
                    count += 1

        with self.output().open('w') as prices_file:
            prices_file.write(str(count))

    def output(self):
        return luigi.LocalTarget('output/inserted-products-{}.json'.format(self.date.strftime('%Y%m%d')))


class InsertPrices(luigi.Task):
    """
    Luigi.Task
    Input: output/branded-products-{date}.json
    Output: output/prices-per-product-{}.json

    Inserta en la base de datos los precios
    de los productos
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        return InsertProductCatalog(date=self.date)

    def run(self):
        count = 1
        with open('output/prices-per-product-{}.json'.format(self.date.strftime('%Y%m%d')), 'r') as prices_file:
            from qqp.api.db.manage import create_qqp_engine
            from qqp.api.db.models import Price
            from sqlalchemy.orm import sessionmaker

            databse_engine = create_qqp_engine()
            Session = sessionmaker(bind=databse_engine)
            db = Session()

            prices = json.load(prices_file)

            for product in prices:
                new_product = Price(
                    id_producto=int(product.get('producto_id')),
                    marca=product.get('marca'),
                    id_marca=int(product.get('id_marca')),
                    id_establecimiento=product.get('idEstablecimiento'),
                    establecimiento=product.get('establecimiento'),
                    direccion=product.get('direccion'),
                    colonia=product.get('colonia'),
                    codigo_postal=product.get('cp'),
                    estado=product.get('estado'),
                    latitud=product.get('latitud'),
                    longitud=product.get('longitud'),
                    precio=product.get('precio'),
                    fecha_observacion=datetime.datetime.strptime(product.get('observacion'), '%d/%m/%Y'),
                    fecha_actualizacion=self.date)
                db.add(new_product)
                db.commit()
                count += 1

        with self.output().open('w') as prices_file:
            prices_file.write(str(count))

    def output(self):
        return luigi.LocalTarget('output/inserted-prices-{}.json'.format(self.date.strftime('%Y%m%d')))


class StartETL(luigi.Task):
    """
    Luigi.Task
    Input: output/prices-per-product-{}.json
    Output: output/SUCCESS-{}.json

    Inicia el pipeline de descarga
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        # return InsertPrices(date=datetime.datetime.strptime('20180518', '%Y%m%d'))
        return InsertPrices(date=self.date)

    def run(self):
        with self.output().open('w') as output_final:
            output_final.write('SUCCESS')

    def output(self):
        return luigi.LocalTarget('output/SUCCESS-{}.json'.format(self.date.strftime('%Y%m%d')))
