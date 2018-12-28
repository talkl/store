from bottle import route, run, template, static_file, get, post, delete, request, HTTPResponse
from sys import argv
import json
import pymysql
import mimetypes
import requests

connection = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='hmtbuktxehutk1!',
                             db='store', charset='utf8', cursorclass=pymysql.cursors.DictCursor)


@post('/store')
@get('/store')
def get_store_front():
    result = {
        'STATUS': None,
        'MSG': None,
        'STORE_NAME': None,
        'STORE_ID': None
    }
    try:
        store_name_param = request.params.get('name')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM store_front"
            cursor.execute(sql)
            r = cursor.fetchone()
            if r and not store_name_param:
                result['STORE_NAME'] = r['store_name']
                result['STORE_ID'] = r['store_id']
            elif r and store_name_param:
                sql = "UPDATE store_front SET store_name='{}' WHERE store_name='{}'".format(store_name_param, r['store_name'])
                cursor.execute(sql)
                connection.commit()
                result['STORE_ID'] = cursor.lastrowid
                result['STORE_NAME'] = store_name_param
            elif not r and store_name_param:
                sql = "INSERT INTO store_front (store_name) VALUES('{}')".format(store_name_param)
                cursor.execute(sql)
                connection.commit()
                result['STORE_ID'] = cursor.lastrowid
                result['STORE_NAME'] = store_name_param
            else:
                sql = "INSERT INTO store_front (store_name) VALUES('{}')".format(
                    'My Store')
                cursor.execute(sql)
                connection.commit()
                result['STORE_ID'] = cursor.lastrowid
                result['STORE_NAME'] = 'My Store'
            result['STATUS'] = 'SUCCESS'
            return HTTPResponse(status=200, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'internal error'
        return HTTPResponse(status=500, body=result)


@get('/category/<id>/products')
@get('/products')
def get_list_of_products(id=id):
    result = {
        'STATUS': None,
        'MSG': None,
        'PRODUCTS': []
    }
    try:
        with connection.cursor() as cursor:
            if isinstance(id, str):
                sql_category_exists = "SELECT * FROM categories WHERE category_id={}".format(int(id))
                cursor.execute(sql_category_exists)
                r = cursor.fetchone()
                if not r:
                    result['STATUS'] = 'ERROR'
                    result['MSG'] = 'category not found'
                    return HTTPResponse(status=404, body=result)
                sql = "SELECT * FROM products WHERE product_category_id={}".format(int(id))
            else:
                sql = "SELECT * FROM products"
            cursor.execute(sql)
            r = cursor.fetchall()
            if not r:
                result['STATUS'] = 'ERROR'
                result['MSG'] = 'products table is empty'
                return HTTPResponse(status=404, body=result)
            else:
                for product in r:
                    new_product_dict = {}
                    new_product_dict['category'] = product['product_category_id']
                    new_product_dict['description'] = product['product_description']
                    new_product_dict['price'] = float(product['product_price'])
                    new_product_dict['title'] = product['product_title']
                    new_product_dict['favorite'] = product['product_is_favorite']
                    new_product_dict['img_url'] = product['product_img_url']
                    new_product_dict['id'] = product['product_id']
                    new_product_dict['created_at'] = str(product['created_at'])
                    result['PRODUCTS'].append(new_product_dict)
                result['PRODUCTS'] = sorted(result['PRODUCTS'], key=lambda k: (k['favorite'] ,str(
                    k['created_at']) ), reverse=True)
                result['STATUS'] = 'SUCCESS'
                return HTTPResponse(status=200, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'internal error'
        return HTTPResponse(status=500, body=result)


@delete('/product/<id>')
def delete_product(id):
    result = {
        'STATUS': None,
        'MSG': None
    }
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM products WHERE product_id={}".format(
                int(id))
            cursor.execute(sql)
            r = cursor.fetchone()
            if not r:
                result['STATUS'] = 'ERROR'
                result['MSG'] = 'Product not found'
                return HTTPResponse(status=404, body=result)
            else:
                sql = 'DELETE FROM products WHERE product_id={} LIMIT 1'.format(
                    int(id))
                cursor.execute(sql)
                connection.commit()
                result['STATUS'] = 'SUCCESS'
                return HTTPResponse(status=201, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'internal error'
        return HTTPResponse(status=500, body=result)


@get('/product/<id>')
def get_product(id):
    result = {
        'STATUS': None,
        'MSG': None,
        'PRODUCT': {
            "category": None,  # int,
            "description": None,  # string,
            "price": None,  # float,
            "title": None,  # string,
            "favorite": None,  # boolean,
            "img_url": None,  # url string,
            "id": None  # int
        }
    }
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM products WHERE product_id={}".format(
                int(id))
            cursor.execute(sql)
            r = cursor.fetchone()
            if not r:
                result['STATUS'] = 'ERROR'
                result['MSG'] = 'Product not found'
                return HTTPResponse(status=404, body=result)
            else:
                result['PRODUCT']['category'] = r['product_category_id']
                result['PRODUCT']['description'] = r['product_description']
                result['PRODUCT']['price'] = float(r['product_price'])
                result['PRODUCT']['title'] = r['product_title']
                result['PRODUCT']['favorite'] = r['product_is_favorite']
                result['PRODUCT']['img_url'] = r['product_img_url']
                result['PRODUCT']['id'] = r['product_id']
                result['PRODUCT']['created_at'] = str(r['created_at'])
                result['STATUS'] = 'SUCCESS'
                return HTTPResponse(status=200, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'internal error'
        return HTTPResponse(status=500, body=result)


def is_url_image(url):
    mimetype, encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))


def check_url(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except:
        return False


def is_image_and_ready(url):
    return is_url_image(url) and check_url(url)


def validate_price(price):
    try:
        float(price)
        return True
    except ValueError:
        return False


@post('/product')
def add_or_update_product():
    result = {
        'STATUS': None,
        'MSG': None,
        'PRODUCT_ID': None
    }
    try:
        product_id = request.params.get('Id')
        product_title = request.params.get('title')
        product_description = request.params.get('desc')
        product_price = request.params.get('price')
        product_img_url = request.params.get('img_url')
        product_category_id = request.params.get('category')
        product_is_favorite = request.params.get('favorite')
        if not validate_price(product_price) or not is_image_and_ready(product_img_url):
            result['STATUS'] = 'ERROR'
            result['MSG'] = 'price only a number. image url only a valid working link'
            return HTTPResponse(status=400, body=result)
        if product_is_favorite:
            product_is_favorite = True
        else:
            product_is_favorite = False
        if not all([product_title, product_description, product_price, product_img_url, product_category_id]):
            result['STATUS'] = 'ERROR'
            result['MSG'] = 'missing parameters'
            return HTTPResponse(status=400, body=result)
        with connection.cursor() as cursor:
            sql = "SELECT * FROM categories WHERE category_id={}".format(int(product_category_id))
            cursor.execute(sql)
            r = cursor.fetchone()
            if not r:
                result['STATUS'] = 'ERROR'
                result['MSG'] = 'Category not found'
                return HTTPResponse(status=404, body=result)
            else:
                # update product
                if product_id:
                    sql = "UPDATE products SET product_id={1}, product_title='{2}', product_description='{3}', product_price={4}, " \
                          "product_img_url='{5}', product_category_id={6}, product_is_favorite={7} WHERE product_id={1}" \
                        .format(int(product_id), product_title, product_description, round(float(product_price), 2),
                                product_img_url, int(product_category_id), product_is_favorite)
                    cursor.execute(sql)
                    connection.commit()
                    result['PRODUCT_ID'] = product_id
                # create product
                else:
                    sql = "INSERT INTO products (product_title, product_description, product_price, " \
                          "product_img_url, product_category_id, product_is_favorite) VALUES ('{}','{}',{},'{}',{},{})" \
                        .format(product_title, product_description, round(float(product_price), 2), product_img_url,
                                int(product_category_id), product_is_favorite)
                    cursor.execute(sql)
                    id = cursor.lastrowid
                    connection.commit()
                    result['PRODUCT_ID'] = id
                result['STATUS'] = 'SUCCESS'
                return HTTPResponse(status=201, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'Internal error'
        return HTTPResponse(status=500, body=result)


@get('/categories')
def list_categories():
    result = {
        'STATUS': None,
        'MSG': None,
        'CATEGORIES': []
    }
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM categories"
            cursor.execute(sql)
            r = cursor.fetchall()
            for category in r:
                result['CATEGORIES'].append({
                    'id': category['category_id'],
                    'name': category['category_name']
                })
        result['STATUS'] = 'SUCCESS'
        return HTTPResponse(status=200, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'Internal error'
        return HTTPResponse(status=500, body=result)


@delete('/category/<id>')
def delete_category(id):
    result = {
        'STATUS': None,
        'MSG': None,
    }
    id_to_delete = id
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM categories WHERE category_id={};".format(int(id_to_delete))
            cursor.execute(sql)
            r = cursor.fetchone()
            if not r:
                result['STATUS'] = 'ERROR'
                result['MSG'] = 'Category not found'
                return HTTPResponse(status=404, body=result)
            else:
                sql = 'DELETE FROM categories WHERE category_id={} LIMIT 1'.format(int(id_to_delete))
                cursor.execute(sql)
                connection.commit()
                result['STATUS'] = 'SUCCESS'
                return HTTPResponse(status=201, body=result)
    except pymysql.IntegrityError:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'Category has products attached. Please delete products first.'
        return HTTPResponse(status=500, body=result)
    except:
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'Internal error'
        return HTTPResponse(status=500, body=result)


@post('/category')
def add_category():
    response = {
        'STATUS': None,
        'MSG': None,
        'CAT_ID': None
    }
    try:
        name_of_category = request.params.get('name')
        if not name_of_category:
            response['STATUS'] = 'ERROR'
            response['MSG'] = 'Name parameter is missing'
            return HTTPResponse(status=400, body=response)
        with connection.cursor() as cursor:
            sql = "SELECT * FROM categories WHERE category_name='{}';".format(name_of_category)
            cursor.execute(sql)
            result = cursor.fetchone()
            if not result:
                response['STATUS'] = 'SUCCESS'
                sql = 'INSERT INTO categories (category_name) VALUES (%s)'
                cursor.execute(sql, name_of_category)
                id = cursor.lastrowid
                connection.commit()
                response['CAT_ID'] = id
                return HTTPResponse(status=201, body=response)
            else:
                response['STATUS'] = 'ERROR'
                response['MSG'] = 'Category already exists'
                return HTTPResponse(status=200, body=response)
    except:
        response['STATUS'] = 'ERROR'
        response['MSG'] = 'Internal error'
        return HTTPResponse(status=500, body=response)


@get("/admin")
def admin_portal():
    return template("pages/admin.html")


@get("/")
def index():
    return template("index.html")


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')


run(host='localhost', port=7000)
