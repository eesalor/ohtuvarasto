"""This module manages multiple warehouses and products using SQLite database."""
import sqlite3
import os
from varasto import Varasto


class WarehouseManager:
    """Manages multiple warehouses and their products using SQLite database."""

    # Predefined products list with default capacities (for fruit warehouses)
    AVAILABLE_PRODUCTS = {
        "Apple": 5.0,
        "Banana": 3.0,
        "Orange": 4.0,
        "Grape": 2.0,
        "Mango": 6.0,
        "Strawberry": 1.5,
        "Watermelon": 10.0,
        "Pineapple": 8.0,
        "Peach": 3.5,
        "Pear": 4.5
    }

    def __init__(self, db_path=None):
        """Initialize the warehouse manager with SQLite database."""
        if db_path is None:
            # Get the directory where this file is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, 'warehouse.db')
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        """Initialize the database with schema."""
        # Get the schema file path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, 'schema.sql')

        conn = self._get_connection()
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
        finally:
            conn.close()

    def name_exists(self, name, exclude_id=None):
        """Check if a warehouse name already exists."""
        conn = self._get_connection()
        try:
            if exclude_id is None:
                cursor = conn.execute(
                    "SELECT id FROM warehouses WHERE LOWER(name) = LOWER(?)",
                    (name,)
                )
            else:
                cursor = conn.execute(
                    "SELECT id FROM warehouses WHERE LOWER(name) = LOWER(?) AND id != ?",
                    (name, exclude_id)
                )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def create_warehouse(self, name, capacity, warehouse_type='fruit'):
        """Create a new warehouse with given name, capacity and type."""
        if self.name_exists(name):
            return None  # Name already exists

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO warehouses (name, capacity, balance, type)
                   VALUES (?, ?, 0.0, ?)""",
                (name, capacity, warehouse_type)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def _build_warehouse_dict(self, row, products):
        """Build a warehouse dictionary from database row."""
        varasto = Varasto(row['capacity'], row['balance'])
        return {
            'id': row['id'],
            'name': row['name'],
            'varasto': varasto,
            'products': products,
            'type': row['type']
        }

    def get_warehouse(self, warehouse_id):
        """Get a warehouse by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM warehouses WHERE id = ?",
                (warehouse_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None

            # Get products for this warehouse
            products_cursor = conn.execute(
                "SELECT name, quantity FROM products WHERE warehouse_id = ?",
                (warehouse_id,)
            )
            products = {p['name']: p['quantity'] for p in products_cursor.fetchall()}

            return self._build_warehouse_dict(row, products)
        finally:
            conn.close()

    def get_all_warehouses(self):
        """Get all warehouses."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM warehouses ORDER BY id")
            warehouses = []
            for row in cursor.fetchall():
                # Get products for this warehouse
                products_cursor = conn.execute(
                    "SELECT name, quantity FROM products WHERE warehouse_id = ?",
                    (row['id'],)
                )
                products = {p['name']: p['quantity'] for p in products_cursor.fetchall()}
                warehouses.append(self._build_warehouse_dict(row, products))
            return warehouses
        finally:
            conn.close()

    def update_warehouse(self, warehouse_id, name, capacity):
        """Update warehouse name and capacity."""
        conn = self._get_connection()
        try:
            # Get current warehouse
            cursor = conn.execute(
                "SELECT * FROM warehouses WHERE id = ?",
                (warehouse_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return False, "Warehouse not found"

            current_balance = row['balance']

            # Check if name already exists (excluding current warehouse)
            if self.name_exists(name, exclude_id=warehouse_id):
                return False, "Name already exists"

            # Check if new capacity is less than current balance
            if capacity < current_balance:
                return False, "Capacity cannot be less than current balance"

            conn.execute(
                """UPDATE warehouses
                   SET name = ?, capacity = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (name, capacity, warehouse_id)
            )
            conn.commit()
            return True, "Success"
        finally:
            conn.close()

    def add_product(self, warehouse_id, product_name, quantity):
        """Add a product to a warehouse."""
        conn = self._get_connection()
        try:
            # Get warehouse
            cursor = conn.execute(
                "SELECT * FROM warehouses WHERE id = ?",
                (warehouse_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return False

            available_space = row['capacity'] - row['balance']

            # Check if we can add the quantity
            if quantity <= available_space:
                # Update warehouse balance
                new_balance = row['balance'] + quantity
                conn.execute(
                    """UPDATE warehouses
                       SET balance = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (new_balance, warehouse_id)
                )

                # Check if product already exists
                product_cursor = conn.execute(
                    "SELECT * FROM products WHERE warehouse_id = ? AND name = ?",
                    (warehouse_id, product_name)
                )
                existing_product = product_cursor.fetchone()

                if existing_product:
                    # Update existing product
                    new_qty = existing_product['quantity'] + quantity
                    conn.execute(
                        """UPDATE products
                           SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                           WHERE warehouse_id = ? AND name = ?""",
                        (new_qty, warehouse_id, product_name)
                    )
                else:
                    # Insert new product
                    conn.execute(
                        """INSERT INTO products (warehouse_id, name, quantity)
                           VALUES (?, ?, ?)""",
                        (warehouse_id, product_name, quantity)
                    )

                conn.commit()
                return True
            return False
        finally:
            conn.close()

    def remove_product(self, warehouse_id, product_name):
        """Remove a product from a warehouse."""
        conn = self._get_connection()
        try:
            # Get product
            cursor = conn.execute(
                "SELECT * FROM products WHERE warehouse_id = ? AND name = ?",
                (warehouse_id, product_name)
            )
            product = cursor.fetchone()
            if product is None:
                return False

            quantity = product['quantity']

            # Update warehouse balance
            conn.execute(
                """UPDATE warehouses
                   SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (quantity, warehouse_id)
            )

            # Delete product
            conn.execute(
                "DELETE FROM products WHERE warehouse_id = ? AND name = ?",
                (warehouse_id, product_name)
            )

            conn.commit()
            return True
        finally:
            conn.close()

    def delete_warehouse(self, warehouse_id):
        """Delete a warehouse."""
        conn = self._get_connection()
        try:
            # Delete products first (foreign key constraint)
            conn.execute(
                "DELETE FROM products WHERE warehouse_id = ?",
                (warehouse_id,)
            )

            # Delete warehouse
            cursor = conn.execute(
                "DELETE FROM warehouses WHERE id = ?",
                (warehouse_id,)
            )

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
