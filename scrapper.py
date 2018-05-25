import time
import datetime
import threading
from threading import Thread
from collections import deque
import requests


class Connector:
    def __init__(self):
        self.http = requests

    def http_get(self, url=None, http_params={}):
        if not url:
            return {}

        print("Thread name:", threading.currentThread().getName())
        print("HTTP Params:")
        print(http_params)

        response = self.http.get(url, params=http_params)
        if response.status_code != 200:
            raise Exception('Error en la peticion http')

        return response.json()

    def http_qqp_extract(self, url=None, http_params={}, second_key='elemento'):
        json_response = self.http_get(url=url, http_params=http_params)
        json_response = list(map(lambda x: x.get(second_key), json_response.get('directory', [])))
        return json_response

    def http_qqp_async(self, url=None, http_params={}, second_key='elemento', queue_output=deque()):
        response = self.http_qqp_extract(url=url, http_params=http_params, second_key='elemento')
        queue_output.extend(response)


class Categories(Connector):
    def __init__(self, *args, **kwargs):
        super(Categories, self).__init__(*args, **kwargs)
        self.update_date = kwargs.get('update_date', datetime.datetime.now())

        # Configuracion para las categorias
        self.main_categories = []
        self.main_categories_url = 'http://200.53.148.112:82/jsonApps/qqp_secciones.aspx'

        # Configuracion para las Sub categorias tipo A
        self.sub_a_categories_url = 'http://200.53.148.112:82/jsonApps/qqp_subseccion1.aspx'

        # Configuracion para las Sub categorias tipo B
        self.sub_b_categories_url = 'http://200.53.148.112:82/jsonApps/qqp_subseccion2.aspx'

    def set_main_categories(self):
        response = self.http_qqp_extract(url=self.main_categories_url)

        print("Categorias")
        def correct_format(category):
            return {'id': category['clave'], 'nombre': category['titulo']}

        for category in response:
            if not category['titulo']:
                del category

        self.main_categories = list(map(correct_format, response))

    def set_verbose_category(self, url=None, http_params={}, queue_output=deque()):
        categories = self.http_qqp_extract(url=url, http_params=http_params, second_key='elemento')
        def correct_format(category):
            if category['titulo']:
                return {'id': category['clave'], 'nombre': category['titulo']}

        queue_output.extend(map(correct_format, categories))

    def set_sub_a_categories(self):
        import concurrent.futures
        queue_task = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for category_id in range(len(self.main_categories)):
                title = self.main_categories[category_id]['nombre']
                if title.strip() != '':
                    print("Armando subcategorias de ", title)
                    self.main_categories[category_id]['subcategoria'] = deque()

                    parameters = {
                        'url': self.sub_a_categories_url,
                        'queue_output': self.main_categories[category_id]['subcategoria'],
                        'http_params': {
                            'seccion': title
                        }
                    }

                    queue_task.append(self.set_verbose_category, **parameters)

            for task in queue_task:
                task.result()

        print(self.main_categories)

    def set_sub_b_categories(self):
        import concurrent.futures
        queue_task = []

        with concurrent.features.ThreadPoolExecutor(max_workers=10) as executor:
            for category_id in range(len(self.main_categories)):
                if self.main_categories[category_id]['nombre']:
                    sub_categories = self.main_categories[category_id]['subcategoria']
                    for sub_category_id in range(len(sub_categories)):
                        title = sub_categories[sub_category_id]['nombre']
                        if title.strip():
                            print("Armando subcategorias B de ", title)
                            self.main_categories[category_id]['subcategoria'][sub_category_id]['subcategoria'] = deque()

                            parameters = {
                                'url': self.sub_b_categories_url,
                                'queue_output': self.main_categories[category_id]['subcategoria'][sub_category_id]['subcategoria'],
                                'http_params': {
                                    'subseccion1': title
                                }
                            }

                            queue_task.append(self.set_verbose_category, **parameters)

            for task in queue_task:
                task.result()

    def make_json_serializable(self):
        for category in self.main_categories:
            if category['nombre']:
                category['subcategoria'] = list(category['subcategoria'])
                for sub_category in category['subcategoria']:
                    sub_category['subcategoria'] = list(sub_category['subcategoria'])
                    for sub_b_category in sub_category['subcategoria']:
                        if sub_b_category.get('subcategoria', None):
                            sub_b_category['subcategoria'] = list(sub_b_category['subcategoria'])


class Geography(Connector):
    def __init__(self, *args, **kwargs):
        super(Geography, self).__init__(*args, **kwargs)
        self.update_date = kwargs.get('update_date', datetime.datetime.now())
        self.cities = []

        # Configuracion
        self.cities_url = 'http://200.53.148.112:82/jsonApps/qqp2.aspx'
        self.regions_url = 'http://200.53.148.112:82/jsonApps/qqp2.aspx'

    def set_states(self):
        params = {
            'url': self.cities_url,
            'http_params': {
                've': 'selecCiudad'
            }
        }

        self.cities = self.http_qqp_extract(**params)

    def set_regions(self):
        import concurrent.futures
        queue_task = []

        with concurrent.features.ThreadPoolExecutor(max_workers=10) as executor:
            for city in self.cities:
                city['municipios'] = deque()
                params = {
                    'url': self.regions_url,
                    'queue_output': city['municipios'],
                    'http_params': {
                        've': 'selecMuni',
                        'idCiudad': city['id']
                    }
                }

                queue_task.append(self.http_qqp_async, **params)

            for task in queue_task:
                task.result()

    def make_json_serializable(self):
        for city in self.cities:
            city['municipios'] = list(city['municipios'])


class Products(Connector):
    def __init__(self, *args, **kwargs):
        self.geography = kwargs.get('geopgraphy', None)
        self.categories = kwargs.get('categories', None)

        self.id_products = deque()
        self.products = deque()
        self.url_products = 'http://200.53.148.112/json/qqp_subseccionInter.php'

        if self.geography:
            kwargs.pop('geopgraphy')

        if self.categories:
            kwargs.pop('categories')

        super(Products, self).__init__(*args, **kwargs)

    def get_async_product(self, url=None, http_params={}):
        products = self.http_qqp_extract(url=url, http_params=http_params)
        print(products)
        for product in products:
            if not product['cveProd'] in self.id_products:
                self.id_products.append(product['cveProd'])
                self.products.append({'id': product['cveProd'], 'nombre': product['Producto']})

    def set_products(self):
        import concurrent.futures
        queue_task = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for city in self.geography:
                for region in city['municipios']:
                    for category in self.categories:
                        if category['nombre']:
                            print(category)
                            for sub_category in category['subcategoria']:
                                for sub_b_category in sub_category['subcategoria']:
                                    parameters = {
                                        'url': self.url_products,
                                        'http_params': {
                                            'qqp_subseccion2': sub_b_category['nombre'],
                                            'idCiudad': city['id'],
                                            'idMunicipio': region['id']
                                        }
                                    }

                                    print(parameters)
                                    queue_task.append(executor.submit(self.get_async_product, **parameters))

            for task in queue_task:
                task.result()

    def make_json_serializable(self):
        self.products = list(self.products)



class Brands(Connector):
    def __init__(self, *args, **kwargs):
        self.geography = kwargs.get('geography', None)
        self.products = kwargs.get('products', None)

        self.id_brands = deque()
        self.brands = deque()
        self.url_brands = 'http://200.53.148.112:82/jsonApps/jsonApps2/qqp_subseccion3.aspx'

        if self.geography:
            kwargs.pop('geography')

        if self.products:
            kwargs.pop('products')

        super(Brands, self).__init__(*args, **kwargs)

    def process_brand_by_product(self, http_params={}, brands_deques=deque(), product=None):
        brands = self.http_qqp_extract(url=self.url_brands, http_params=http_params)
        for brand in brands:
            if '{0}-{1}'.format(product, brand['cve_categoria']) not in self.id_brands:
                self.id_brands.append('{0}-{1}'.format(product, brand['cve_categoria']))
                brands_deques.append({'id': brand['cve_categoria'], 'marca': brand['titulo']})

    def set_brands_by_product(self):
        import concurrent.futures
        queue_task = []

        print(len(self.products))
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for product in self.products:
                for city in self.geography:
                    regions = '-'.join(map(lambda x: x['id'], city['municipios']))
                    if not product.get('marcas', False):
                        product['marcas'] = deque()

                    parameters = {
                        'http_params': {
                            'cveProducto': product['id'],
                            'idCiudad': city['id'],
                            'idMunicipio': regions
                        },
                        'product': product['id'],
                        'brands_deques': product['marcas']
                    }

                    queue_task.append(executor.submit(self.process_brand_by_product, **parameters))

            for task in queue_task:
                task.result()


    def make_json_serializable(self):
        for product in self.products:
            if product.get('marcas', False):
                product['marcas'] = list(product['marcas'])


class Prices(Connector):
    def __init__(self, *args, **kwargs):
        self.products = kwargs.get('products', None)
        self.geography = kwargs.get('geography', None)
        self.date = kwargs.get('date', datetime.date.today())
        self.prices = deque()

        self.url = 'http://200.53.148.112/json/listaEst.php'

        if self.products:
            kwargs.pop('products')

        if self.geography:
            kwargs.pop('geography')

        kwargs.pop('date')
        super(Prices, self).__init__(*args, **kwargs)

    def download_prices(self, http_params={}, product_id=None, brand=None):
        if product_id and brand:
            prices = self.http_qqp_extract(http_params=http_params, url=self.url)
            for product in prices:
                self.prices.append({'producto': {'producto_id': product_id, 'marca': brand}.update(product), 'date': self.date.strftime('%Y%m%d')})

    def get_prices_per_product(self):
        import concurrent.futures
        queue_task = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            for product in self.products:
                for city in self.geography:
                    regions = '-'.join(map(lambda x: x['id'], city['municipios']))
                    for brand in product['marcas']:

                        parameters = {
                            'http_params': {
                                'idMunicipio': regions,
                                'idCiudad': city['id'],
                                'idProducto': product['id'],
                                'idMarca': brand['id']
                            },
                            'product_id': product['id'],
                            'brand': brand['id']
                        }

                        # queue_task.append({})
                        queue_task.append(executor.submit(self.download_prices, **parameters))

        print("Numero de tareas ...")
        print(len(queue_task))
        # time.sleep(5)
        for thread_price in queue_task:
            thread_price.result()

    def get_prices(self):
        return list(self.prices)

if __name__ == "__main__":
    qqp_scrapper = Categories()
    qqp_geograpy = Geography()

    qqp_scrapper.set_main_categories()
    qqp_scrapper.set_sub_a_categories()
    qqp_scrapper.set_sub_b_categories()
    qqp_geograpy.set_states()
    qqp_geograpy.set_regions()

    print(qqp_scrapper.main_categories)
    print(qqp_geograpy.cities)

    qqp_products = Products(geopgraphy=qqp_geograpy.cities, categories=qqp_scrapper.main_categories)
    qqp_products.set_products()
    print(len(qqp_products.products))

    qqp_brands = Brands(geopgraphy=qqp_geograpy.cities, categories=qqp_scrapper.main_categories, products=qqp_products.products)
