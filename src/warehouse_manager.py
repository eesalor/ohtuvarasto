"""Manages multiple warehouses and products using SQLite database."""
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
                query = """SELECT id FROM warehouses
                           WHERE LOWER(name) = LOWER(?) AND id != ?"""
                cursor = conn.execute(query, (name, exclude_id))
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
            products = {
                p['name']: p['quantity'] for p in products_cursor.fetchall()
            }

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
                query = """SELECT name, quantity FROM products
                           WHERE warehouse_id = ?"""
                products_cursor = conn.execute(query, (row['id'],))
                products = {
                    p['name']: p['quantity'] for p in products_cursor.fetchall()
                }
                warehouses.append(self._build_warehouse_dict(row, products))
            return warehouses
        finally:
            conn.close()

    def _validate_update(self, conn, warehouse_id, name, capacity):
        """Validate warehouse update parameters."""
        cursor = conn.execute(
            "SELECT * FROM warehouses WHERE id = ?",
            (warehouse_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None, "Warehouse not found"

        if self.name_exists(name, exclude_id=warehouse_id):
            return None, "Name already exists"

        if capacity < row['balance']:
            return None, "Capacity cannot be less than current balance"

        return row, None

    def update_warehouse(self, warehouse_id, name, capacity):
        """Update warehouse name and capacity."""
        conn = self._get_connection()
        try:
            _, error = self._validate_update(
                conn, warehouse_id, name, capacity
            )
            if error:
                return False, error

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

    def _update_warehouse_balance(self, conn, warehouse_id, new_balance):
        """Update warehouse balance."""
        conn.execute(
            """UPDATE warehouses
               SET balance = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (new_balance, warehouse_id)
        )

    def _upsert_product(self, conn, warehouse_id, product_name, quantity):
        """Insert or update a product in the warehouse."""
        query = """SELECT * FROM products
                   WHERE warehouse_id = ? AND name = ?"""
        cursor = conn.execute(query, (warehouse_id, product_name))
        existing = cursor.fetchone()

        if existing:
            new_qty = existing['quantity'] + quantity
            conn.execute(
                """UPDATE products
                   SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE warehouse_id = ? AND name = ?""",
                (new_qty, warehouse_id, product_name)
            )
        else:
            conn.execute(
                """INSERT INTO products (warehouse_id, name, quantity)
                   VALUES (?, ?, ?)""",
                (warehouse_id, product_name, quantity)
            )

    def _get_warehouse(self, conn, warehouse_id):
        """Get a warehouse by ID from the database."""
        cursor = conn.execute(
            "SELECT * FROM warehouses WHERE id = ?",
            (warehouse_id,)
        )
        return cursor.fetchone()

    def add_product(self, warehouse_id, product_name, quantity):
        """Add a product to a warehouse."""
        conn = self._get_connection()
        try:
            row = self._get_warehouse(conn, warehouse_id)
            if row is None or quantity > row['capacity'] - row['balance']:
                return False

            new_balance = row['balance'] + quantity
            self._update_warehouse_balance(conn, warehouse_id, new_balance)
            self._upsert_product(conn, warehouse_id, product_name, quantity)
            conn.commit()
            return True
        finally:
            conn.close()

    def _get_product(self, conn, warehouse_id, product_name):
        """Get a product from the database."""
        cursor = conn.execute(
            "SELECT * FROM products WHERE warehouse_id = ? AND name = ?",
            (warehouse_id, product_name)
        )
        return cursor.fetchone()

    def remove_product(self, warehouse_id, product_name):
        """Remove a product from a warehouse."""
        conn = self._get_connection()
        try:
            product = self._get_product(conn, warehouse_id, product_name)
            if product is None:
                return False

            conn.execute(
                """UPDATE warehouses
                   SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (product['quantity'], warehouse_id)
            )
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
