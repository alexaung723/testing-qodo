const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

// In-memory user storage (in real app, this would be a database)
let users = new Map();

// Initialize with some demo users
users.set('demo-user-1', {
  id: 'demo-user-1',
  email: 'john.doe@example.com',
  username: 'johndoe',
  firstName: 'John',
  lastName: 'Doe',
  phone: '+1-555-0123',
  address: {
    street: '123 Main St',
    city: 'Anytown',
    state: 'CA',
    zipCode: '90210',
    country: 'USA'
  },
  preferences: {
    newsletter: true,
    marketing: false,
    language: 'en',
    currency: 'USD'
  },
  createdAt: '2024-01-15T10:00:00Z',
  updatedAt: '2024-01-15T10:00:00Z'
});

users.set('demo-user-2', {
  id: 'demo-user-2',
  email: 'jane.smith@example.com',
  username: 'janesmith',
  firstName: 'Jane',
  lastName: 'Smith',
  phone: '+1-555-0456',
  address: {
    street: '456 Oak Ave',
    city: 'Somewhere',
    state: 'NY',
    zipCode: '10001',
    country: 'USA'
  },
  preferences: {
    newsletter: false,
    marketing: true,
    language: 'en',
    currency: 'USD'
  },
  createdAt: '2024-01-20T14:30:00Z',
  updatedAt: '2024-01-20T14:30:00Z'
});

// Get all users (admin only in real app)
router.get('/', (req, res) => {
  try {
    const { limit = 50, offset = 0, search } = req.query;
    
    let userList = Array.from(users.values());
    
    // Search functionality
    if (search) {
      const searchLower = search.toLowerCase();
      userList = userList.filter(user =>
        user.email.toLowerCase().includes(searchLower) ||
        user.username.toLowerCase().includes(searchLower) ||
        user.firstName.toLowerCase().includes(searchLower) ||
        user.lastName.toLowerCase().includes(searchLower)
      );
    }
    
    // Pagination
    const total = userList.length;
    const paginatedUsers = userList.slice(parseInt(offset), parseInt(offset) + parseInt(limit));
    
    res.json({
      success: true,
      data: paginatedUsers,
      pagination: {
        total,
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: parseInt(offset) + parseInt(limit) < total
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get user by ID
router.get('/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    const user = users.get(userId);
    
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    res.json({
      success: true,
      data: user
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Create new user
router.post('/', (req, res) => {
  try {
    const { email, username, firstName, lastName, phone, address, preferences } = req.body;
    
    // Basic validation
    if (!email || !username || !firstName || !lastName) {
      return res.status(400).json({ 
        success: false, 
        error: 'Email, username, first name, and last name are required' 
      });
    }
    
    // Check if email or username already exists
    const existingUser = Array.from(users.values()).find(u => 
      u.email === email || u.username === username
    );
    
    if (existingUser) {
      return res.status(409).json({ 
        success: false, 
        error: 'User with this email or username already exists' 
      });
    }
    
    const userId = uuidv4();
    const now = new Date().toISOString();
    
    const newUser = {
      id: userId,
      email,
      username,
      firstName,
      lastName,
      phone: phone || null,
      address: address || null,
      preferences: {
        newsletter: false,
        marketing: false,
        language: 'en',
        currency: 'USD',
        ...preferences
      },
      createdAt: now,
      updatedAt: now
    };
    
    users.set(userId, newUser);
    
    res.status(201).json({
      success: true,
      data: newUser,
      message: 'User created successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Update user
router.put('/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    const updateData = req.body;
    
    const user = users.get(userId);
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    // Fields that can be updated
    const allowedFields = ['firstName', 'lastName', 'phone', 'address', 'preferences'];
    const updates = {};
    
    allowedFields.forEach(field => {
      if (updateData[field] !== undefined) {
        updates[field] = updateData[field];
      }
    });
    
    // Check for email/username conflicts if updating those fields
    if (updateData.email && updateData.email !== user.email) {
      const emailExists = Array.from(users.values()).some(u => 
        u.id !== userId && u.email === updateData.email
      );
      if (emailExists) {
        return res.status(409).json({ 
          success: false, 
          error: 'Email already in use by another user' 
        });
      }
      updates.email = updateData.email;
    }
    
    if (updateData.username && updateData.username !== user.username) {
      const usernameExists = Array.from(users.values()).some(u => 
        u.id !== userId && u.username === updateData.username
      );
      if (usernameExists) {
        return res.status(409).json({ 
          success: false, 
          error: 'Username already in use by another user' 
        });
      }
      updates.username = updateData.username;
    }
    
    // Apply updates
    const updatedUser = { ...user, ...updates, updatedAt: new Date().toISOString() };
    users.set(userId, updatedUser);
    
    res.json({
      success: true,
      data: updatedUser,
      message: 'User updated successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Delete user
router.delete('/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    
    const user = users.get(userId);
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    users.delete(userId);
    
    res.json({
      success: true,
      message: 'User deleted successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get user profile
router.get('/:userId/profile', (req, res) => {
  try {
    const { userId } = req.params;
    const user = users.get(userId);
    
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    // Return profile without sensitive information
    const profile = {
      id: user.id,
      username: user.username,
      firstName: user.firstName,
      lastName: user.lastName,
      preferences: user.preferences,
      createdAt: user.createdAt
    };
    
    res.json({
      success: true,
      data: profile
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Update user preferences
router.patch('/:userId/preferences', (req, res) => {
  try {
    const { userId } = req.params;
    const preferences = req.body;
    
    const user = users.get(userId);
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    // Update preferences
    const updatedUser = {
      ...user,
      preferences: { ...user.preferences, ...preferences },
      updatedAt: new Date().toISOString()
    };
    
    users.set(userId, updatedUser);
    
    res.json({
      success: true,
      data: updatedUser.preferences,
      message: 'Preferences updated successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
