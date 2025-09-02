const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

// In-memory order storage (in real app, this would be a database)
let orders = new Map();

// Create new order
router.post('/', (req, res) => {
  try {
    const { userId, items, shippingAddress, paymentMethod } = req.body;
    
    if (!userId || !items || !shippingAddress) {
      return res.status(400).json({ 
        success: false, 
        error: 'User ID, items, and shipping address are required' 
      });
    }
    
    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Items must be a non-empty array' 
      });
    }
    
    // Calculate order total (in real app, you'd fetch actual product prices)
    const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax = total * 0.08; // 8% tax
    const shipping = total > 50 ? 0 : 5.99; // Free shipping over $50
    const grandTotal = total + tax + shipping;
    
    const order = {
      id: uuidv4(),
      userId,
      items: items.map(item => ({
        ...item,
        id: uuidv4()
      })),
      shippingAddress,
      paymentMethod: paymentMethod || 'credit_card',
      subtotal: total,
      tax,
      shipping,
      total: grandTotal,
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      estimatedDelivery: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days from now
    };
    
    // Store order
    if (!orders.has(userId)) {
      orders.set(userId, []);
    }
    orders.get(userId).push(order);
    
    res.status(201).json({
      success: true,
      data: order,
      message: 'Order created successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get user's orders
router.get('/user/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    const userOrders = orders.get(userId) || [];
    
    // Sort by creation date (newest first)
    userOrders.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    
    res.json({
      success: true,
      data: userOrders,
      total: userOrders.length
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get order by ID
router.get('/:orderId', (req, res) => {
  try {
    const { orderId } = req.params;
    let foundOrder = null;
    
    // Search through all orders to find the specific order
    for (const [userId, userOrders] of orders.entries()) {
      const order = userOrders.find(o => o.id === orderId);
      if (order) {
        foundOrder = order;
        break;
      }
    }
    
    if (!foundOrder) {
      return res.status(404).json({ success: false, error: 'Order not found' });
    }
    
    res.json({
      success: true,
      data: foundOrder
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Update order status
router.patch('/:orderId/status', (req, res) => {
  try {
    const { orderId } = req.params;
    const { status } = req.body;
    
    if (!status) {
      return res.status(400).json({ 
        success: false, 
        error: 'Status is required' 
      });
    }
    
    const validStatuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ 
        success: false, 
        error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` 
      });
    }
    
    let foundOrder = null;
    let foundUserId = null;
    
    // Find the order
    for (const [userId, userOrders] of orders.entries()) {
      const orderIndex = userOrders.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        foundOrder = userOrders[orderIndex];
        foundUserId = userId;
        break;
      }
    }
    
    if (!foundOrder) {
      return res.status(404).json({ success: false, error: 'Order not found' });
    }
    
    // Update status
    foundOrder.status = status;
    foundOrder.updatedAt = new Date().toISOString();
    
    // Update estimated delivery for shipped orders
    if (status === 'shipped') {
      foundOrder.estimatedDelivery = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(); // 3 days from now
    }
    
    res.json({
      success: true,
      data: foundOrder,
      message: 'Order status updated successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Cancel order
router.patch('/:orderId/cancel', (req, res) => {
  try {
    const { orderId } = req.params;
    const { reason } = req.body;
    
    let foundOrder = null;
    let foundUserId = null;
    
    // Find the order
    for (const [userId, userOrders] of orders.entries()) {
      const orderIndex = userOrders.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        foundOrder = userOrders[orderIndex];
        foundUserId = userId;
        break;
      }
    }
    
    if (!foundOrder) {
      return res.status(404).json({ success: false, error: 'Order not found' });
    }
    
    // Check if order can be cancelled
    if (['shipped', 'delivered'].includes(foundOrder.status)) {
      return res.status(400).json({ 
        success: false, 
        error: 'Cannot cancel order that has already been shipped or delivered' 
      });
    }
    
    // Cancel order
    foundOrder.status = 'cancelled';
    foundOrder.updatedAt = new Date().toISOString();
    foundOrder.cancellationReason = reason || 'Cancelled by user';
    
    res.json({
      success: true,
      data: foundOrder,
      message: 'Order cancelled successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get order statistics
router.get('/stats/overview', (req, res) => {
  try {
    let totalOrders = 0;
    let totalRevenue = 0;
    let statusCounts = {
      pending: 0,
      confirmed: 0,
      processing: 0,
      shipped: 0,
      delivered: 0,
      cancelled: 0
    };
    
    // Aggregate statistics from all orders
    for (const [userId, userOrders] of orders.entries()) {
      totalOrders += userOrders.length;
      userOrders.forEach(order => {
        totalRevenue += order.total;
        statusCounts[order.status]++;
      });
    }
    
    res.json({
      success: true,
      data: {
        totalOrders,
        totalRevenue: Math.round(totalRevenue * 100) / 100,
        statusCounts,
        averageOrderValue: totalOrders > 0 ? Math.round((totalRevenue / totalOrders) * 100) / 100 : 0
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
