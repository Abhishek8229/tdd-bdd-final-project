######################################################################
# Copyright 2016, 2023 John J. Rofrano.
# All Rights Reserved.
######################################################################
"""
Product API Service Test Suite
"""
import os
import logging
from decimal import Decimal
from unittest import TestCase

from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/products"


######################################################################
#  TEST CASES
######################################################################
class TestProductRoutes(TestCase):
    """Product Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """Runs after each test"""
        db.session.remove()

    ##################################################################
    # Utility
    ##################################################################
    def _create_products(self, count=1):
        products = []
        for _ in range(count):
            product = ProductFactory()
            response = self.client.post(BASE_URL, json=product.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            product.id = new_product["id"]
            products.append(product)
        return products

    ##################################################################
    # TESTS
    ##################################################################

    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["message"], "OK")

    # ----------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a Product"""
        product = ProductFactory()
        response = self.client.post(BASE_URL, json=product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(Decimal(data["price"]), product.price)
        self.assertEqual(data["available"], product.available)
        self.assertEqual(data["category"], product.category.name)

    def test_create_product_missing_name(self):
        """It should not create a product without a name"""
        product = ProductFactory().serialize()
        del product["name"]
        response = self.client.post(BASE_URL, json=product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not create without content-type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ----------------------------------------------------------
    # READ
    # ----------------------------------------------------------
    def test_get_product(self):
        """It should Read a Product"""
        product = self._create_products()[0]
        response = self.client.get(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["id"], product.id)

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------
    def test_update_product(self):
        """It should Update a Product"""
        product = self._create_products()[0]
        updated = product.serialize()
        updated["description"] = "Updated description"

        response = self.client.put(f"{BASE_URL}/{product.id}", json=updated)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["description"], "Updated description")

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------
    def test_delete_product(self):
        """It should Delete a Product"""
        product = self._create_products()[0]
        response = self.client.delete(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # LIST ALL
    # ----------------------------------------------------------
    def test_list_all_products(self):
        """It should list all products"""
        self._create_products(3)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.get_json()), 3)

    # ----------------------------------------------------------
    # QUERY BY NAME
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should query products by name"""
        products = self._create_products(5)
        name = products[0].name

        response = self.client.get(BASE_URL, query_string=f"name={name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.get_json():
            self.assertEqual(product["name"], name)

    # ----------------------------------------------------------
    # QUERY BY CATEGORY
    # ----------------------------------------------------------
    def test_query_by_category(self):
        """It should query products by category"""
        products = self._create_products(5)
        category = products[0].category.name

        response = self.client.get(BASE_URL, query_string=f"category={category}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.get_json():
            self.assertEqual(product["category"], category)

    # ----------------------------------------------------------
    # QUERY BY AVAILABILITY
    # ----------------------------------------------------------
    def test_query_by_availability(self):
        """It should query products by availability"""
        products = self._create_products(5)
        available = products[0].available

        response = self.client.get(BASE_URL, query_string=f"available={available}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.get_json():
            self.assertEqual(product["available"], available)

