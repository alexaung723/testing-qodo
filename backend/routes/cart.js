const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

// In-memory cart storage (in real app, this would be a database)
let carts = new Map();

// Get cart by user ID
router.get('/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    const cart = carts.get(userId) || { items: [], total: 0, itemCount: 0 };
    
    res.json({
      success: true,
      data: cart
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Add item to cart
router.post('/:userId/items', (req, res) => {
  try {
    const { userId } = req.params;
    const { productId, quantity = 1 } = req.body;
    
    if (!productId || quantity < 1) {
      return res.status(400).json({ 
        success: false, 
        error: 'Product ID and quantity (min 1) are required' 
      });
    }
    
    // Get or create cart
    let cart = carts.get(userId);
    if (!cart) {
      cart = { items: [], total: 0, itemCount: 0 };
    }
    
    // Check if item already exists in cart
    const existingItemIndex = cart.items.findIndex(item => item.productId === productId);
    
    if (existingItemIndex >= 0) {
      // Update existing item quantity
      cart.items[existingItemIndex].quantity += quantity;
    } else {
      // Add new item (in real app, you'd fetch product details from database)
      cart.items.push({
        id: uuidv4(),
        productId,
        quantity,
        addedAt: new Date().toISOString()
      });
    }
    
    // Recalculate totals
    cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    // Note: In real app, you'd calculate total based on actual product prices
    
    carts.set(userId, cart);
    
    res.json({
      success: true,
      data: cart,
      message: 'Item added to cart successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Update item quantity in cart
router.put('/:userId/items/:itemId', (req, res) => {
  try {
    const { userId, itemId } = req.params;
    const { quantity } = req.body;
    
    if (quantity < 1) {
      return res.status(400).json({ 
        success: false, 
        error: 'Quantity must be at least 1' 
      });
    }
    
    const cart = carts.get(userId);
    if (!cart) {
      return res.status(404).json({ success: false, error: 'Cart not found' });
    }
    
    const itemIndex = cart.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      return res.status(404).json({ success: false, error: 'Item not found in cart' });
    }
    
    cart.items[itemIndex].quantity = quantity;
    cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    
    carts.set(userId, cart);
    
    res.json({
      success: true,
      data: cart,
      message: 'Cart updated successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Remove item from cart
router.delete('/:userId/items/:itemId', (req, res) => {
  try {
    const { userId, itemId } = req.params;
    
    const cart = carts.get(userId);
    if (!cart) {
      return res.status(404).json({ success: false, error: 'Cart not found' });
    }
    
    const itemIndex = cart.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      return res.status(404).json({ success: false, error: 'Item not found in cart' });
    }
    
    cart.items.splice(itemIndex, 1);
    cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    
    carts.set(userId, cart);
    
    res.json({
      success: true,
      data: cart,
      message: 'Item removed from cart successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Clear entire cart
router.delete('/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    
    carts.delete(userId);
    
    res.json({
      success: true,
      message: 'Cart cleared successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get cart summary (item count, total)
router.get('/:userId/summary', (req, res) => {
  try {
    const { userId } = req.params;
    const cart = carts.get(userId) || { items: [], total: 0, itemCount: 0 };
    
    res.json({
      success: true,
      data: {
        itemCount: cart.itemCount,
        total: cart.total,
        itemCount: cart.items.length
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
