const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

// In-memory product storage (in real app, this would be a database)
let products = [
  {
    id: '1',
    name: 'Wireless Bluetooth Headphones',
    description: 'High-quality wireless headphones with noise cancellation',
    price: 129.99,
    category: 'Electronics',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
    stock: 25,
    rating: 4.5,
    reviews: 128,
    tags: ['wireless', 'bluetooth', 'noise-cancelling', 'audio']
  },
  {
    id: '2',
    name: 'Organic Cotton T-Shirt',
    description: 'Comfortable organic cotton t-shirt, available in multiple colors',
    price: 24.99,
    category: 'Clothing',
    image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400',
    stock: 50,
    rating: 4.2,
    reviews: 89,
    tags: ['organic', 'cotton', 'comfortable', 'sustainable']
  },
  {
    id: '3',
    name: 'Smart Fitness Watch',
    description: 'Track your fitness goals with this advanced smartwatch',
    price: 199.99,
    category: 'Electronics',
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',
    stock: 15,
    rating: 4.7,
    reviews: 256,
    tags: ['fitness', 'smartwatch', 'health', 'tracking']
  },
  {
    id: '4',
    name: 'Stainless Steel Water Bottle',
    description: 'Keep your drinks cold for 24 hours with this insulated bottle',
    price: 19.99,
    category: 'Home & Garden',
    image: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400',
    stock: 100,
    rating: 4.4,
    reviews: 203,
    tags: ['insulated', 'stainless-steel', 'eco-friendly', 'durable']
  },
  {
    id: '5',
    name: 'Professional Chef Knife Set',
    description: 'Complete set of professional-grade kitchen knives',
    price: 89.99,
    category: 'Home & Garden',
    image: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400',
    stock: 30,
    rating: 4.8,
    reviews: 167,
    tags: ['professional', 'kitchen', 'sharp', 'durable']
  }
];

// Get all products
router.get('/', (req, res) => {
  try {
    const { category, search, minPrice, maxPrice, sortBy, limit = 20 } = req.query;
    
    let filteredProducts = [...products];
    
    // Filter by category
    if (category) {
      filteredProducts = filteredProducts.filter(p => 
        p.category.toLowerCase() === category.toLowerCase()
      );
    }
    
    // Search by name or description
    if (search) {
      const searchLower = search.toLowerCase();
      filteredProducts = filteredProducts.filter(p =>
        p.name.toLowerCase().includes(searchLower) ||
        p.description.toLowerCase().includes(searchLower) ||
        p.tags.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }
    
    // Filter by price range
    if (minPrice) {
      filteredProducts = filteredProducts.filter(p => p.price >= parseFloat(minPrice));
    }
    if (maxPrice) {
      filteredProducts = filteredProducts.filter(p => p.price <= parseFloat(maxPrice));
    }
    
    // Sort products
    if (sortBy) {
      switch (sortBy) {
        case 'price-low':
          filteredProducts.sort((a, b) => a.price - b.price);
          break;
        case 'price-high':
          filteredProducts.sort((a, b) => b.price - a.price);
          break;
        case 'rating':
          filteredProducts.sort((a, b) => b.rating - a.rating);
          break;
        case 'reviews':
          filteredProducts.sort((a, b) => b.reviews - a.reviews);
          break;
        case 'name':
          filteredProducts.sort((a, b) => a.name.localeCompare(b.name));
          break;
      }
    }
    
    // Apply limit
    if (limit) {
      filteredProducts = filteredProducts.slice(0, parseInt(limit));
    }
    
    res.json({
      success: true,
      data: filteredProducts,
      total: filteredProducts.length,
      filters: { category, search, minPrice, maxPrice, sortBy, limit }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get product by ID
router.get('/:id', (req, res) => {
  try {
    const product = products.find(p => p.id === req.params.id);
    if (!product) {
      return res.status(404).json({ success: false, error: 'Product not found' });
    }
    res.json({ success: true, data: product });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get product categories
router.get('/categories/list', (req, res) => {
  try {
    const categories = [...new Set(products.map(p => p.category))];
    res.json({ success: true, data: categories });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get featured products (high rating, good stock)
router.get('/featured/list', (req, res) => {
  try {
    const featured = products
      .filter(p => p.rating >= 4.0 && p.stock > 10)
      .sort((a, b) => b.rating - a.rating)
      .slice(0, 6);
    
    res.json({ success: true, data: featured });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
