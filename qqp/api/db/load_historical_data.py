import csv
import json
from sqlalchemy.orm import sessionmaker
from qqp.api.db.manage import create_qqp_engine
from qqp.api.db.models import Product, Price


def read_big_csv():
    with open('all_data.csv', 'r') as historic_data:
        datareader = csv.reader(historic_data)
        next(datareader)

        for row in datareader:
            yield list(row)


def read_json_products():
    with open('branded-products-20180709.json','r') as json_brand:
        hash_table = {}
        json_obj = json.load(json_brand)
        print(type(json_obj))

        # json_obj = sorted(json_obj, key=lambda product: product['nombre'])
        for product in json_obj:
            hash_table[product['nombre']] = product

        return hash_table


def binary_search(list_work, value, length, start, end, counter):
    middle = (start + end) // 2
    letter = list_work[middle]['nombre'][:length].lower()

    print("valor:", value)
    print("letra:", letter)
    print("length", length)
    print("middle", middle)
    print("start", start)
    print("end", end)

    if counter == 10:
        return ""

    if len(list_work) < 11:
        print([ele['nombre'] for ele in list_work])

    if middle == start and middle == end and value != list_work[middle]['nombre']:
        return ""

    if middle == len(list_work) and value == list_work[middle]['nombre']:
        return list_work[middle]

    # print(middle)
    if value[:length].lower() > letter:
        return binary_search(list_work, value, length, middle, end, counter + 1)
    elif value[:length].lower() < letter:
        return binary_search(list_work, value, length, start, middle, counter + 1)
    elif letter == value[:length].lower():
        if length == len(value):
            return list_work[middle]
        else:
            length =+ 1
            return binary_search(list_work, value, length, start, end, counter + 1)
    else:
        return ''

if __name__ == "__main__":
    databse_engine = create_qqp_engine()
    migrate(databse_engine)
    Session = sessionmaker(bind=databse_engine)
    db = Session()

    counter = 0
    json_products = read_json_products()

    for row in read_big_csv():
        if counter > 100:
            break

        if not json_products.get(row[0]):
            new_product = Product(
                nombre=row[0],
                id_profeco='1012{}'.format(counter),
                catalogo=row[4],
                categoria=row[3]
            )
            db.add(new_product)
            current_product = {
                'nombre': row[0],
                'id': '1012{}'.format(counter),
                'catalogo': row[4],
                'categoria': row[3]
            }
        else:
            current_product = json_products.get(row[0])


        Price(
            id_producto=int(current_product.get('id')),
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
        counter += 1
