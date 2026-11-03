######################################################################
# Product Store Service with UI
######################################################################
from decimal import InvalidOperation
from flask import jsonify, request, abort, url_for
from service.models import Product, Category, DataValidationError
from service.common import status
from . import app


@app.route("/health")
def healthcheck():
    """Health check endpoint."""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


@app.route("/")
def index():
    """Serve the product catalog home page."""
    return app.send_static_file("index.html")


def check_content_type(content_type):
    """Ensure the request has the expected content type."""
    if request.headers.get("Content-Type") != content_type:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")


@app.route("/products", methods=["POST"])
def create_products():
    """Create a product from the JSON request body."""
    check_content_type("application/json")
    product = Product()
    try:
        product.deserialize(request.get_json())
        product.create()
    except (DataValidationError, InvalidOperation, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))
    location_url = url_for("get_product", product_id=product.id, _external=True)
    return jsonify(product.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/products", methods=["GET"])
def list_products():
    """List all products or filter by name, category, or availability."""
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")
    products = Product.all()

    if name:
        products = Product.find_by_name(name)
    if category:
        try:
            products = Product.find_by_category(Category[category.upper()])
        except KeyError:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid category: {category}")
    if available is not None:
        value = available.strip().lower()
        if value not in ("true", "false"):
            abort(status.HTTP_400_BAD_REQUEST, "available must be true or false")
        products = Product.find_by_availability(value == "true")

    return jsonify([product.serialize() for product in products]), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Read a product by its ID."""
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found")
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Update an existing product."""
    check_content_type("application/json")
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found")
    try:
        product.deserialize(request.get_json())
        product.id = product_id
        product.update()
    except (DataValidationError, InvalidOperation, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product by its ID."""
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found")
    product.delete()
    return "", status.HTTP_204_NO_CONTENT
