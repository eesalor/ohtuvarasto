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
        
        if name and capacity > 0:
            manager.create_warehouse(name, capacity)
            flash('Warehouse created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid warehouse data!', 'error')
    
    return render_template('create_warehouse.html')


@app.route('/edit/<int:warehouse_id>', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit a warehouse."""
    warehouse = manager.get_warehouse(warehouse_id)
    
    if not warehouse:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = float(request.form.get('capacity'))
        
        if name and capacity > 0:
            manager.update_warehouse(warehouse_id, name, capacity)
            flash('Warehouse updated successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid warehouse data!', 'error')
    
    return render_template('edit_warehouse.html', warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    """View warehouse details and manage products."""
    warehouse = manager.get_warehouse(warehouse_id)
    
    if not warehouse:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))
    
    available_products = WarehouseManager.AVAILABLE_PRODUCTS
    return render_template('view_warehouse.html', 
                         warehouse=warehouse,
                         available_products=available_products)


@app.route('/warehouse/<int:warehouse_id>/add_product', methods=['POST'])
def add_product(warehouse_id):
    """Add a product to a warehouse."""
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
    app.run(debug=True)
