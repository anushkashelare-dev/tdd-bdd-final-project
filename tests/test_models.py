# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """It should Read a Product by id."""
        product = ProductFactory()
        product.create()

        found = Product.find(product.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(Decimal(found.price), product.price)

    def test_update_a_product(self):
        """It should Update a Product description without changing its id."""
        product = ProductFactory()
        product.create()
        original_id = product.id

        product.description = "Updated description"
        product.update()

        found = Product.find(original_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.description, "Updated description")
        self.assertEqual(found.id, original_id)

    def test_delete_a_product(self):
        """It should Delete a Product and update the database count."""
        count_before = len(Product.all())
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), count_before + 1)

        product.delete()

        self.assertEqual(len(Product.all()), count_before)
        self.assertIsNone(Product.find(product.id))

    def test_list_all_products(self):
        """It should List all Products."""
        self.assertEqual(Product.all(), [])

        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()

        found = Product.all()
        self.assertEqual(len(found), 3)
        self.assertEqual(
            {item.name for item in found},
            {item.name for item in products}
        )

    def test_find_product_by_name(self):
        """It should Find all Products with a specific name."""
        products = ProductFactory.create_batch(3, name="Unique Widget")
        other_product = ProductFactory(name="Different Widget")
        for product in products + [other_product]:
            product.create()

        found = Product.find_by_name("Unique Widget").all()

        self.assertEqual(len(found), 3)
        self.assertTrue(all(item.name == "Unique Widget" for item in found))

    def test_find_products_by_category(self):
        """It should Find Products by category."""
        matching_products = ProductFactory.create_batch(3, category=Category.TOOLS)
        other_products = ProductFactory.create_batch(2, category=Category.CLOTHS)
        for product in matching_products + other_products:
            product.create()

        found = Product.find_by_category(Category.TOOLS).all()

        self.assertEqual(len(found), 3)
        self.assertTrue(all(item.category == Category.TOOLS for item in found))

    def test_find_products_by_availability(self):
        """It should Find Products by availability."""
        available_products = ProductFactory.create_batch(3, available=True)
        unavailable_products = ProductFactory.create_batch(2, available=False)
        for product in available_products + unavailable_products:
            product.create()

        found = Product.find_by_availability(True).all()

        self.assertEqual(len(found), 3)
        self.assertTrue(all(item.available is True for item in found))
