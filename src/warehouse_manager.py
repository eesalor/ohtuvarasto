"""This module manages multiple warehouses and products."""
from varasto import Varasto


class WarehouseManager:
    """Manages multiple warehouses and their products."""
    
    # Predefined products list with default capacities
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
    
    def __init__(self):
        """Initialize the warehouse manager."""
        self.warehouses = {}
        self.warehouse_id_counter = 1
    
    def create_warehouse(self, name, capacity):
        """Create a new warehouse with given name and capacity."""
        warehouse_id = self.warehouse_id_counter
        self.warehouses[warehouse_id] = {
            'id': warehouse_id,
            'name': name,
            'varasto': Varasto(capacity),
            'products': {}  # {product_name: quantity}
        }
        self.warehouse_id_counter += 1
        return warehouse_id
    
    def get_warehouse(self, warehouse_id):
        """Get a warehouse by ID."""
        return self.warehouses.get(warehouse_id)
    
    def get_all_warehouses(self):
        """Get all warehouses."""
        return list(self.warehouses.values())
    
    def update_warehouse(self, warehouse_id, name, capacity):
        """Update warehouse name and capacity."""
        if warehouse_id in self.warehouses:
            warehouse = self.warehouses[warehouse_id]
            warehouse['name'] = name
            
            # Create new Varasto with new capacity and existing balance
            old_varasto = warehouse['varasto']
            new_varasto = Varasto(capacity, old_varasto.saldo)
            warehouse['varasto'] = new_varasto
            return True
        return False
    
    def add_product(self, warehouse_id, product_name, quantity):
        """Add a product to a warehouse."""
        if warehouse_id in self.warehouses:
            warehouse = self.warehouses[warehouse_id]
            varasto = warehouse['varasto']
            
            # Check if we can add the quantity
            if quantity <= varasto.paljonko_mahtuu():
                varasto.lisaa_varastoon(quantity)
                
                # Track the product
                if product_name in warehouse['products']:
                    warehouse['products'][product_name] += quantity
                else:
                    warehouse['products'][product_name] = quantity
                return True
        return False
    
    def remove_product(self, warehouse_id, product_name):
        """Remove a product from a warehouse."""
        if warehouse_id in self.warehouses:
            warehouse = self.warehouses[warehouse_id]
            
            if product_name in warehouse['products']:
                quantity = warehouse['products'][product_name]
                warehouse['varasto'].ota_varastosta(quantity)
                del warehouse['products'][product_name]
                return True
        return False
    
    def delete_warehouse(self, warehouse_id):
        """Delete a warehouse."""
        if warehouse_id in self.warehouses:
            del self.warehouses[warehouse_id]
            return True
        return False
