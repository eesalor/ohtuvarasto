"""Unit tests for WarehouseManager class."""
import unittest
import tempfile
import os
import sqlite3
from warehouse_manager import WarehouseManager


class TestWarehouseManager(unittest.TestCase):
    """Tests for WarehouseManager class."""

    def setUp(self):
        """Set up test fixtures with temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(
            suffix='.db', delete=False
        )
        self.temp_db.close()
        self.manager = WarehouseManager(db_path=self.temp_db.name)

    def tearDown(self):
        """Clean up temporary database."""
        os.unlink(self.temp_db.name)

    def test_create_warehouse(self):
        """Test creating a warehouse."""
        wh_id = self.manager.create_warehouse("Test Warehouse", 100.0)
        self.assertIsNotNone(wh_id)

    def test_create_warehouse_with_type(self):
        """Test creating a warehouse with custom type."""
        wh_id = self.manager.create_warehouse("Custom", 50.0, "custom")
        warehouse = self.manager.get_warehouse(wh_id)
        self.assertEqual(warehouse['type'], 'custom')

    def test_create_warehouse_duplicate_name(self):
        """Test creating a warehouse with duplicate name fails."""
        self.manager.create_warehouse("Duplicate", 100.0)
        result = self.manager.create_warehouse("Duplicate", 200.0)
        self.assertIsNone(result)

    def test_get_warehouse(self):
        """Test getting a warehouse by ID."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        warehouse = self.manager.get_warehouse(wh_id)
        self.assertEqual(warehouse['name'], 'Test')
        self.assertAlmostEqual(warehouse['varasto'].tilavuus, 100.0)

    def test_get_warehouse_not_found(self):
        """Test getting a non-existent warehouse."""
        warehouse = self.manager.get_warehouse(999)
        self.assertIsNone(warehouse)

    def test_get_all_warehouses(self):
        """Test getting all warehouses."""
        self.manager.create_warehouse("First", 100.0)
        self.manager.create_warehouse("Second", 200.0)
        warehouses = self.manager.get_all_warehouses()
        self.assertEqual(len(warehouses), 2)

    def test_name_exists_true(self):
        """Test name_exists returns True for existing name."""
        self.manager.create_warehouse("Existing", 100.0)
        self.assertTrue(self.manager.name_exists("Existing"))

    def test_name_exists_false(self):
        """Test name_exists returns False for non-existing name."""
        self.assertFalse(self.manager.name_exists("Nonexistent"))

    def test_name_exists_with_exclude_id(self):
        """Test name_exists with exclude_id parameter."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.assertFalse(self.manager.name_exists("Test", exclude_id=wh_id))

    def test_update_warehouse(self):
        """Test updating warehouse name and capacity."""
        wh_id = self.manager.create_warehouse("Original", 100.0)
        success, message = self.manager.update_warehouse(wh_id, "Updated", 150)
        self.assertTrue(success)
        self.assertEqual(message, "Success")

    def test_update_warehouse_not_found(self):
        """Test updating non-existent warehouse."""
        success, message = self.manager.update_warehouse(999, "Test", 100.0)
        self.assertFalse(success)
        self.assertEqual(message, "Warehouse not found")

    def test_update_warehouse_duplicate_name(self):
        """Test updating warehouse to existing name fails."""
        self.manager.create_warehouse("First", 100.0)
        wh_id = self.manager.create_warehouse("Second", 100.0)
        success, message = self.manager.update_warehouse(wh_id, "First", 100)
        self.assertFalse(success)
        self.assertEqual(message, "Name already exists")

    def test_update_warehouse_capacity_less_than_balance(self):
        """Test updating capacity less than balance fails."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.manager.add_product(wh_id, "Apple", 50.0)
        success, msg = self.manager.update_warehouse(wh_id, "Test", 30.0)
        self.assertFalse(success)
        self.assertEqual(msg, "Capacity cannot be less than current balance")

    def test_add_product(self):
        """Test adding a product to warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        result = self.manager.add_product(wh_id, "Apple", 10.0)
        self.assertTrue(result)

    def test_add_product_updates_existing(self):
        """Test adding product updates existing product quantity."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.manager.add_product(wh_id, "Apple", 10.0)
        self.manager.add_product(wh_id, "Apple", 5.0)
        warehouse = self.manager.get_warehouse(wh_id)
        self.assertAlmostEqual(warehouse['products']['Apple'], 15.0)

    def test_add_product_exceeds_capacity(self):
        """Test adding product that exceeds capacity fails."""
        wh_id = self.manager.create_warehouse("Test", 10.0)
        result = self.manager.add_product(wh_id, "Apple", 20.0)
        self.assertFalse(result)

    def test_add_product_warehouse_not_found(self):
        """Test adding product to non-existent warehouse fails."""
        result = self.manager.add_product(999, "Apple", 10.0)
        self.assertFalse(result)

    def test_remove_product(self):
        """Test removing a product from warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.manager.add_product(wh_id, "Apple", 10.0)
        result = self.manager.remove_product(wh_id, "Apple")
        self.assertTrue(result)

    def test_remove_product_not_found(self):
        """Test removing non-existent product fails."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        result = self.manager.remove_product(wh_id, "Nonexistent")
        self.assertFalse(result)

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        result = self.manager.delete_warehouse(wh_id)
        self.assertTrue(result)

    def test_delete_warehouse_not_found(self):
        """Test deleting non-existent warehouse fails."""
        result = self.manager.delete_warehouse(999)
        self.assertFalse(result)

    def test_delete_warehouse_with_products(self):
        """Test deleting warehouse also removes products."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.manager.add_product(wh_id, "Apple", 10.0)
        result = self.manager.delete_warehouse(wh_id)
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_warehouse(wh_id))

    def test_available_products_exists(self):
        """Test AVAILABLE_PRODUCTS class attribute exists."""
        self.assertIn("Apple", WarehouseManager.AVAILABLE_PRODUCTS)

    def test_default_db_path(self):
        """Test manager initializes with default db path."""
        manager = WarehouseManager()
        self.assertIsNotNone(manager.db_path)
        self.assertTrue(manager.db_path.endswith('warehouse.db'))

    def test_create_warehouse_integrity_error(self):
        """Test IntegrityError handling during warehouse creation."""
        from unittest import mock

        with mock.patch.object(
            self.manager, 'name_exists', return_value=False
        ):
            with mock.patch.object(
                self.manager, '_get_connection'
            ) as mock_conn:
                mock_cursor = mock.MagicMock()
                mock_cursor.execute.side_effect = sqlite3.IntegrityError
                mock_conn.return_value = mock_cursor
                result = self.manager.create_warehouse("Test", 100.0)
                self.assertIsNone(result)
