import pandas as pd
from pathlib import Path

def test_generator_runs():
    from src.data.generator import (
        generate_material_master,
        generate_customer_master,
        generate_stock_levels
    )
    materials = generate_material_master(10)
    assert len(materials) == 10
    assert "material_id" in materials.columns

def test_material_id_format():
    from src.data.generator import generate_material_master
    materials = generate_material_master(5)
    for mid in materials["material_id"]:
        assert mid.startswith("MAT-")

def test_customer_id_format():
    from src.data.generator import generate_customer_master
    customers = generate_customer_master(5)
    for cid in customers["customer_id"]:
        assert cid.startswith("CUST-")

def test_stock_levels_generated():
    from src.data.generator import generate_material_master, generate_stock_levels
    materials = generate_material_master(10)
    stock     = generate_stock_levels(materials)
    assert len(stock) == len(materials)
    assert "below_safety" in stock.columns
    assert "needs_reorder" in stock.columns

def test_sales_orders_generated():
    from src.data.generator import (
        generate_material_master,
        generate_customer_master,
        generate_sales_orders
    )
    materials = generate_material_master(10)
    customers = generate_customer_master(5)
    orders    = generate_sales_orders(customers, materials, 20)
    assert len(orders) == 20
    assert "total_value" in orders.columns
    assert "currency" in orders.columns

def test_currency_is_eur():
    from src.data.generator import generate_customer_master
    customers = generate_customer_master(5)
    assert (customers["currency"] == "EUR").all()