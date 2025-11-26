"""Unit tests for Flask web application."""
import unittest
import tempfile
import os
from app import app, _parse_float
from warehouse_manager import WarehouseManager


class TestApp(unittest.TestCase):
    """Tests for Flask application."""

    def setUp(self):
        """Set up test client and temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(
            suffix='.db', delete=False
        )
        self.temp_db.close()

        # Create test manager and replace global manager
        import app as app_module
        self.original_manager = app_module.manager
        app_module.manager = WarehouseManager(db_path=self.temp_db.name)
        self.manager = app_module.manager

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def tearDown(self):
        """Clean up temporary database and restore manager."""
        import app as app_module
        app_module.manager = self.original_manager
        os.unlink(self.temp_db.name)

    def test_index(self):
        """Test index page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_create_warehouse_get(self):
        """Test create warehouse page GET."""
        response = self.client.get('/create')
        self.assertEqual(response.status_code, 200)

    def test_create_warehouse_post_success(self):
        """Test creating a warehouse successfully."""
        response = self.client.post('/create', data={
            'name': 'Test Warehouse',
            'capacity': '100',
            'warehouse_type': 'fruit'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_create_warehouse_post_invalid_data(self):
        """Test creating a warehouse with invalid data."""
        response = self.client.post('/create', data={
            'name': '',
            'capacity': '100'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_create_warehouse_post_invalid_capacity(self):
        """Test creating a warehouse with invalid capacity."""
        response = self.client.post('/create', data={
            'name': 'Test',
            'capacity': '-10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_create_warehouse_duplicate_name(self):
        """Test creating a warehouse with duplicate name."""
        self.manager.create_warehouse("Existing", 100.0)
        response = self.client.post('/create', data={
            'name': 'Existing',
            'capacity': '100',
            'warehouse_type': 'fruit'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse(self):
        """Test viewing a warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.get(f'/warehouse/{wh_id}')
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse_not_found(self):
        """Test viewing non-existent warehouse."""
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse_post_update(self):
        """Test updating warehouse via POST."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.post(f'/warehouse/{wh_id}', data={
            'update_warehouse': 'true',
            'name': 'Updated',
            'capacity': '150'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse_post_update_invalid(self):
        """Test updating warehouse with invalid data."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.post(f'/warehouse/{wh_id}', data={
            'update_warehouse': 'true',
            'name': '',
            'capacity': '150'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse_update_duplicate_name(self):
        """Test updating warehouse to duplicate name."""
        self.manager.create_warehouse("First", 100.0)
        wh_id = self.manager.create_warehouse("Second", 100.0)
        response = self.client.post(f'/warehouse/{wh_id}', data={
            'update_warehouse': 'true',
            'name': 'First',
            'capacity': '100'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse_update_capacity_too_low(self):
        """Test updating warehouse capacity below balance."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.manager.add_product(wh_id, "Apple", 50.0)
        response = self.client.post(f'/warehouse/{wh_id}', data={
            'update_warehouse': 'true',
            'name': 'Test',
            'capacity': '30'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_product_success(self):
        """Test adding a product to warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.post(f'/warehouse/{wh_id}/add_product', data={
            'product_name': 'Apple',
            'quantity': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_product_not_found(self):
        """Test adding product to non-existent warehouse."""
        response = self.client.post(
            '/warehouse/999/add_product',
            data={'product_name': 'Apple', 'quantity': '10'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_add_product_invalid_data(self):
        """Test adding product with invalid data."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.post(f'/warehouse/{wh_id}/add_product', data={
            'product_name': '',
            'quantity': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_product_exceeds_capacity(self):
        """Test adding product that exceeds capacity."""
        wh_id = self.manager.create_warehouse("Test", 10.0)
        response = self.client.post(f'/warehouse/{wh_id}/add_product', data={
            'product_name': 'Apple',
            'quantity': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_product_custom_warehouse(self):
        """Test adding custom product to custom warehouse."""
        wh_id = self.manager.create_warehouse("Custom", 100.0, "custom")
        response = self.client.post(f'/warehouse/{wh_id}/add_product', data={
            'custom_product_name': 'CustomProduct',
            'quantity': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_remove_product_success(self):
        """Test removing a product from warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        self.manager.add_product(wh_id, "Apple", 10.0)
        response = self.client.post(
            f'/warehouse/{wh_id}/remove_product/Apple',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_product_not_found(self):
        """Test removing non-existent product."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.post(
            f'/warehouse/{wh_id}/remove_product/Nonexistent',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_warehouse_success(self):
        """Test deleting a warehouse."""
        wh_id = self.manager.create_warehouse("Test", 100.0)
        response = self.client.post(
            f'/warehouse/{wh_id}/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_warehouse_not_found(self):
        """Test deleting non-existent warehouse."""
        response = self.client.post(
            '/warehouse/999/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)


class TestParseFloat(unittest.TestCase):
    """Tests for _parse_float helper function."""

    def test_parse_float_valid(self):
        """Test parsing valid float string."""
        result = _parse_float('10.5')
        self.assertAlmostEqual(result, 10.5)

    def test_parse_float_integer(self):
        """Test parsing integer string."""
        result = _parse_float('10')
        self.assertAlmostEqual(result, 10.0)

    def test_parse_float_empty(self):
        """Test parsing empty string."""
        result = _parse_float('')
        self.assertIsNone(result)

    def test_parse_float_none(self):
        """Test parsing None."""
        result = _parse_float(None)
        self.assertIsNone(result)

    def test_parse_float_invalid(self):
        """Test parsing invalid string."""
        result = _parse_float('abc')
        self.assertIsNone(result)


class TestFlashUpdateResult(unittest.TestCase):
    """Tests for _flash_update_result helper function."""

    def test_flash_update_result_generic_error(self):
        """Test generic error message flash."""
        from app import _flash_update_result
        with app.test_request_context():
            _flash_update_result(False, "Unknown error")


class TestMain(unittest.TestCase):
    """Tests for main module functionality."""

    def test_app_exists(self):
        """Test the Flask app is properly configured."""
        self.assertIsNotNone(app)
        self.assertEqual(app.secret_key, 'warehouse-secret-key-12345')
