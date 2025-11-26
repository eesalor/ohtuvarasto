"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for, flash
from warehouse_manager import WarehouseManager

app = Flask(__name__)
app.secret_key = 'warehouse-secret-key-12345'

# Global warehouse manager instance
manager = WarehouseManager()


def _parse_float(value):
    """Parse a float value from form input, returning None on failure."""
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None


def _handle_create_post():
    """Handle POST request for warehouse creation."""
    name = request.form.get('name')
    capacity = _parse_float(request.form.get('capacity'))
    warehouse_type = request.form.get('warehouse_type', 'fruit')

    if not (name and capacity and capacity > 0):
        flash('Invalid warehouse data!', 'error')
        return None

    wh_id = manager.create_warehouse(name, capacity, warehouse_type)
    if wh_id:
        flash('Warehouse created successfully!', 'success')
        return redirect(url_for('index'))

    flash('A warehouse with this name already exists!', 'error')
    return None


@app.route('/')
def index():
    """Display all warehouses."""
    warehouses = manager.get_all_warehouses()
    return render_template('index.html', warehouses=warehouses)


@app.route('/create', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == 'POST':
        result = _handle_create_post()
        if result:
            return result

    return render_template('create_warehouse.html')


def _flash_update_result(success, message):
    """Flash appropriate message for warehouse update result."""
    if success:
        flash('Warehouse updated successfully!', 'success')
    elif message == "Name already exists":
        flash('A warehouse with this name already exists!', 'error')
    elif message == "Capacity cannot be less than current balance":
        flash('Capacity cannot be less than current balance!', 'error')
    else:
        flash('Could not update warehouse!', 'error')


def _handle_warehouse_update(warehouse_id):
    """Handle warehouse update from POST request."""
    name = request.form.get('name')
    capacity = _parse_float(request.form.get('capacity'))

    if not (name and capacity and capacity > 0):
        flash('Invalid warehouse data!', 'error')
        return

    success, message = manager.update_warehouse(warehouse_id, name, capacity)
    _flash_update_result(success, message)


@app.route('/warehouse/<int:warehouse_id>', methods=['GET', 'POST'])
def view_warehouse(warehouse_id):
    """View warehouse details, edit capacity, and manage products."""
    warehouse = manager.get_warehouse(warehouse_id)

    if not warehouse:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST' and 'update_warehouse' in request.form:
        _handle_warehouse_update(warehouse_id)
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    available_products = WarehouseManager.AVAILABLE_PRODUCTS
    warehouse_type = warehouse.get('type', 'fruit')
    return render_template('view_warehouse.html',
                           warehouse=warehouse,
                           available_products=available_products,
                           warehouse_type=warehouse_type)


def _get_product_name(warehouse):
    """Get product name from request form based on warehouse type."""
    warehouse_type = warehouse.get('type', 'fruit')
    if warehouse_type == 'custom':
        return request.form.get('custom_product_name')
    return request.form.get('product_name')


def _handle_add_product(warehouse_id, product_name, quantity):
    """Handle product addition and flash result."""
    if manager.add_product(warehouse_id, product_name, quantity):
        flash(f'Added {quantity} units of {product_name}!', 'success')
    else:
        flash('Could not add product. Check warehouse capacity!', 'error')


@app.route('/warehouse/<int:warehouse_id>/add_product', methods=['POST'])
def add_product(warehouse_id):
    """Add a product to a warehouse."""
    warehouse = manager.get_warehouse(warehouse_id)
    if not warehouse:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    product_name = _get_product_name(warehouse)
    quantity = _parse_float(request.form.get('quantity'))

    if product_name and quantity and quantity > 0:
        _handle_add_product(warehouse_id, product_name, quantity)
    else:
        flash('Invalid product data!', 'error')

    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove_product/<product_name>',
           methods=['POST'])
def remove_product(warehouse_id, product_name):
    """Remove a product from a warehouse."""
    if manager.remove_product(warehouse_id, product_name):
        flash(f'Removed {product_name}!', 'success')
    else:
        flash('Could not remove product!', 'error')

    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    if manager.delete_warehouse(warehouse_id):
        flash('Warehouse deleted successfully!', 'success')
    else:
        flash('Could not delete warehouse!', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
