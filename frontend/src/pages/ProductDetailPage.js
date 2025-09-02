import React, { useState, useEffect } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Button,
  Card,
  CardMedia,
  Rating,
  Chip,
  Divider,
  TextField,
  Alert,
  Skeleton,
  Breadcrumbs,
  Link,
  Paper
} from '@mui/material';
import {
  ShoppingCart as CartIcon,
  ArrowBack as ArrowBackIcon,
  LocalShipping as ShippingIcon,
  Security as SecurityIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';

const ProductDetailPage = () => {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [addToCartLoading, setAddToCartLoading] = useState(false);
  const [addToCartSuccess, setAddToCartSuccess] = useState(false);
  const { addToCart } = useCart();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/products/${productId}`);
        if (response.data.success) {
          setProduct(response.data.data);
        }
      } catch (err) {
        console.error('Error fetching product:', err);
        setError('Failed to load product details');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  const handleAddToCart = async () => {
    try {
      setAddToCartLoading(true);
      await addToCart('demo-user-1', productId, quantity);
      setAddToCartSuccess(true);
      setTimeout(() => setAddToCartSuccess(false), 3000);
    } catch (err) {
      console.error('Error adding to cart:', err);
    } finally {
      setAddToCartLoading(false);
    }
  };

  const handleQuantityChange = (event) => {
    const value = parseInt(event.target.value);
    if (value > 0 && value <= (product?.stock || 1)) {
      setQuantity(value);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Skeleton variant="rectangular" height={400} />
          </Grid>
          <Grid item xs={12} md={6}>
            <Skeleton variant="text" width="80%" height={40} />
            <Skeleton variant="text" width="60%" height={24} />
            <Skeleton variant="text" width="40%" height={32} />
            <Skeleton variant="text" width="100%" height={100} />
            <Skeleton variant="rectangular" width={200} height={48} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (error || !product) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || 'Product not found'}
        </Alert>
        <Button
          component={RouterLink}
          to="/products"
          startIcon={<ArrowBackIcon />}
        >
          Back to Products
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Breadcrumbs */}
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs aria-label="breadcrumb">
          <Link component={RouterLink} to="/" color="inherit" underline="hover">
            Home
          </Link>
          <Link component={RouterLink} to="/products" color="inherit" underline="hover">
            Products
          </Link>
          <Typography color="text.primary">{product.name}</Typography>
        </Breadcrumbs>
      </Box>

      {/* Product Details */}
      <Grid container spacing={4}>
        {/* Product Image */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardMedia
              component="img"
              height="400"
              image={product.image}
              alt={product.name}
              sx={{ objectFit: 'cover' }}
            />
          </Card>
        </Grid>

        {/* Product Info */}
        <Grid item xs={12} md={6}>
          <Box>
            {/* Product Name */}
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              {product.name}
            </Typography>

            {/* Rating and Reviews */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Rating value={product.rating} precision={0.1} size="large" readOnly />
              <Typography variant="body1" sx={{ ml: 1 }}>
                {product.rating} ({product.reviews} reviews)
              </Typography>
            </Box>

            {/* Price */}
            <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold', mb: 2 }}>
              ${product.price}
            </Typography>

            {/* Category */}
            <Chip 
              label={product.category} 
              color="primary" 
              variant="outlined"
              sx={{ mb: 2 }}
            />

            {/* Description */}
            <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.6 }}>
              {product.description}
            </Typography>

            {/* Stock Status */}
            <Box sx={{ mb: 3 }}>
              <Typography 
                variant="body1" 
                color={product.stock > 10 ? 'success.main' : product.stock > 0 ? 'warning.main' : 'error.main'}
                sx={{ fontWeight: 500 }}
              >
                {product.stock > 10 
                  ? `In Stock (${product.stock} available)`
                  : product.stock > 0 
                    ? `Low Stock (${product.stock} left)`
                    : 'Out of Stock'
                }
              </Typography>
            </Box>

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Tags:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {product.tags.map((tag) => (
                    <Chip key={tag} label={tag} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
            )}

            {/* Add to Cart Section */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Add to Cart
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                <TextField
                  type="number"
                  label="Quantity"
                  value={quantity}
                  onChange={handleQuantityChange}
                  inputProps={{ min: 1, max: product.stock }}
                  sx={{ width: 100 }}
                />
                <Typography variant="body2" color="text.secondary">
                  of {product.stock} available
                </Typography>
              </Box>

              <Button
                variant="contained"
                size="large"
                startIcon={<CartIcon />}
                onClick={handleAddToCart}
                disabled={addToCartLoading || product.stock === 0}
                fullWidth
                sx={{ mb: 2 }}
              >
                {addToCartLoading ? 'Adding...' : 'Add to Cart'}
              </Button>

              {addToCartSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Product added to cart successfully!
                </Alert>
              )}

              {product.stock === 0 && (
                <Alert severity="warning">
                  This product is currently out of stock
                </Alert>
              )}
            </Paper>

            {/* Features */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Features & Benefits
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ShippingIcon color="primary" />
                    <Typography variant="body2">Free Shipping</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SecurityIcon color="primary" />
                    <Typography variant="body2">Secure Payment</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <RefreshIcon color="primary" />
                    <Typography variant="body2">Easy Returns</Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Box>
        </Grid>
      </Grid>

      {/* Back Button */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Button
          component={RouterLink}
          to="/products"
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          size="large"
        >
          Back to Products
        </Button>
      </Box>
    </Container>
  );
};

export default ProductDetailPage;
