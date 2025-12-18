# Copyright 2016, 2023 John J. Rofrano.
# All Rights Reserved.

"""
Test cases for Product Model
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
#  PRODUCT MODEL TEST CASES
######################################################################
class TestProductModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ Set up once before all tests """
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.app_context().push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """ Clean up once after all tests """
        db.session.close()
        db.drop_all()

    def setUp(self):
        """ Runs before each test """
        db.session.query(Product).delete()
        db.session.commit()
        self.logger = logging.getLogger("test")

    def tearDown(self):
        """ Runs after each test """
        db.session.remove()

    ##################################################################
    #  TESTS
    ##################################################################

    def test_create_a_product(self):
        """ Test Create a Product """
        product = ProductFactory()
        self.logger.info("Testing create product %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

    def test_read_a_product(self):
        """ Test Read a Product """
        product = ProductFactory()
        product.id = None
        product.create()

        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.available, product.available)
        self.assertEqual(found.category, product.category)

    def test_update_a_product(self):
        """ Test Update a Product """
        product = ProductFactory()
        product.id = None
        product.create()

        product.description = "Updated Description"
        product.update()

        found = Product.find(product.id)
        self.assertEqual(found.description, "Updated Description")

    def test_delete_a_product(self):
        """ Test Delete a Product """
        product = ProductFactory()
        product.id = None
        product.create()

        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """ Test List All Products """
        self.assertEqual(len(Product.all()), 0)
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """ Test Find by Name """
        products = ProductFactory.create_batch(5)
        for product in products:
            product.id = None
            product.create()

        name = products[0].name
        count = sum(1 for p in products if p.name == name)

        found = Product.find_by_name(name)
        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_category(self):
        """ Test Find by Category """
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()

        category = products[0].category
        count = sum(1 for p in products if p.category == category)

        found = Product.find_by_category(category)
        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_availability(self):
        """ Test Find by Availability """
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()

        available = products[0].available
        count = sum(1 for p in products if p.available == available)

        found = Product.find_by_availability(available)
        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.available, available)

