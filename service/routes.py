######################################################################
# Product Routes
######################################################################
from flask import request, jsonify, abort
from service.models import Product, Category
from service.common import status
from service import app
import logging

logger = logging.getLogger(__name__)


######################################################################
# INDEX
######################################################################
@app.route("/")
def index():
    return "Product Catalog Administration", status.HTTP_200_OK


######################################################################
# HEALTH
######################################################################
@app.route("/health")
def health():
    return jsonify(message="OK"), status.HTTP_200_OK


######################################################################
# CREATE PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    if not request.is_json:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    data = request.get_json()
    product = Product()
    product.deserialize(data)
    product.create()
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": f"/products/{product.id}"},
    )


######################################################################
# LIST + QUERY PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        products = Product.find_by_name(name)
    elif category:
        products = Product.find_by_category(Category[category])
    elif available:
        products = Product.find_by_availability(available.lower() == "true")
    else:
        products = Product.all()

    return jsonify([p.serialize() for p in products]), status.HTTP_200_OK


######################################################################
# READ PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND)

    data = request.get_json()
    product.deserialize(data)
    product.update()
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND)

    product.delete()
    return "", status.HTTP_204_NO_CONTENT

