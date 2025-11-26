"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for, flash
from warehouse_manager import WarehouseManager

app = Flask(__name__)
app.secret_key = 'warehouse-secret-key-12345'

# Global warehouse manager instance
manager = WarehouseManager()


@app.route('/')
def index():
    """Display all warehouses."""
    warehouses = manager.get_all_warehouses()
    return render_template('index.html', warehouses=warehouses)


@app.route('/create', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = float(request.form.get('capacity'))
        warehouse_type = request.form.get('warehouse_type', 'fruit')

        if name and capacity > 0:
            warehouse_id = manager.create_warehouse(name, capacity, warehouse_type)
            if warehouse_id:
                flash('Warehouse created successfully!', 'success')
                return redirect(url_for('index'))
            flash('A warehouse with this name already exists!', 'error')
        else:
            flash('Invalid warehouse data!', 'error')

    return render_template('create_warehouse.html')


@app.route('/warehouse/<int:warehouse_id>', methods=['GET', 'POST'])
def view_warehouse(warehouse_id):
    """View warehouse details, edit capacity, and manage products."""
    warehouse = manager.get_warehouse(warehouse_id)

    if not warehouse:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    # Handle capacity/name update
    if request.method == 'POST' and 'update_warehouse' in request.form:
        name = request.form.get('name')
        capacity = float(request.form.get('capacity'))

        if name and capacity > 0:
            success, message = manager.update_warehouse(warehouse_id, name, capacity)
            if success:
                flash('Warehouse updated successfully!', 'success')
            elif message == "Name already exists":
                flash('A warehouse with this name already exists!', 'error')
            elif message == "Capacity cannot be less than current balance":
                flash('Capacity cannot be less than current balance!', 'error')
            else:
                flash('Could not update warehouse!', 'error')
        else:
            flash('Invalid warehouse data!', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    available_products = WarehouseManager.AVAILABLE_PRODUCTS
    warehouse_type = warehouse.get('type', 'fruit')
    return render_template('view_warehouse.html',
                           warehouse=warehouse,
                           available_products=available_products,
                           warehouse_type=warehouse_type)


@app.route('/warehouse/<int:warehouse_id>/add_product', methods=['POST'])
def add_product(warehouse_id):
    """Add a product to a warehouse."""
    warehouse = manager.get_warehouse(warehouse_id)
    if not warehouse:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    warehouse_type = warehouse.get('type', 'fruit')

    if warehouse_type == 'custom':
        product_name = request.form.get('custom_product_name')
    else:
        product_name = request.form.get('product_name')

    quantity = float(request.form.get('quantity'))

    if product_name and quantity > 0:
        if manager.add_product(warehouse_id, product_name, quantity):
            flash(f'Added {quantity} units of {product_name}!', 'success')
        else:
            flash('Could not add product. Check warehouse capacity!', 'error')
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
