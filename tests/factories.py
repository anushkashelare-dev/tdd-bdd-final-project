# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
# Licensed under the Apache License, Version 2.0
"""Test factories for Product objects."""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import Product, Category


class ProductFactory(factory.Factory):
    """Creates fake products for testing."""

    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Product-{n}")
    description = factory.Faker("sentence", nb_words=4)
    price = FuzzyDecimal(1.00, 500.00, precision=2)
    available = FuzzyChoice([True, False])
    category = FuzzyChoice(list(Category))
