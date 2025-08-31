import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  IconButton,
  TextField,
  Divider,
  Alert,
  Skeleton,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextareaAutosize
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Delete as DeleteIcon,
  ShoppingCart as CartIcon,
  ArrowForward as ArrowIcon,
  LocalShipping as ShippingIcon,
  Payment as PaymentIcon
} from '@mui/icons-material';
import { useCart } from '../contexts/CartContext';
import axios from 'axios';

const CartPage = ({ currentUser }) => {
  const { items, itemCount, loading, fetchCart, updateItemQuantity, removeFromCart, clearCart } = useCart();
  const [products, setProducts] = useState({});
  const [checkoutDialog, setCheckoutDialog] = useState(false);
  const [checkoutForm, setCheckoutForm] = useState({
    shippingAddress: {
      street: '',
      city: '',
      state: '',
      zipCode: '',
      country: 'USA'
    },
    paymentMethod: 'credit_card',
    notes: ''
  });

  useEffect(() => {
    if (currentUser) {
      fetchCart(currentUser);
    }
  }, [currentUser, fetchCart]);

  useEffect(() => {
    const fetchProductDetails = async () => {
      const productIds = [...new Set(items.map(item => item.productId))];
      const productDetails = {};
      
      for (const productId of productIds) {
        try {
          const response = await axios.get(`/api/products/${productId}`);
          if (response.data.success) {
            productDetails[productId] = response.data.data;
          }
        } catch (error) {
          console.error(`Error fetching product ${productId}:`, error);
        }
      }
      
      setProducts(productDetails);
    };

    if (items.length > 0) {
      fetchProductDetails();
    }
  }, [items]);

  const handleQuantityChange = async (itemId, newQuantity) => {
    if (newQuantity > 0) {
      await updateItemQuantity(currentUser, itemId, newQuantity);
    }
  };

  const handleRemoveItem = async (itemId) => {
    await removeFromCart(currentUser, itemId);
  };

  const handleClearCart = async () => {
    await clearCart(currentUser);
  };

  const calculateSubtotal = () => {
    return items.reduce((total, item) => {
      const product = products[item.productId];
      return total + (product?.price || 0) * item.quantity;
    }, 0);
  };

  const calculateTax = () => {
    return calculateSubtotal() * 0.08; // 8% tax
  };

  const calculateShipping = () => {
    const subtotal = calculateSubtotal();
    return subtotal > 50 ? 0 : 5.99; // Free shipping over $50
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax() + calculateShipping();
  };

  const handleCheckout = async () => {
    try {
      const orderItems = items.map(item => {
        const product = products[item.productId];
        return {
          id: item.id,
          productId: item.productId,
          name: product?.name || 'Unknown Product',
          price: product?.price || 0,
          quantity: item.quantity
        };
      });

      const orderData = {
        userId: currentUser,
        items: orderItems,
        shippingAddress: checkoutForm.shippingAddress,
        paymentMethod: checkoutForm.paymentMethod
      };

      const response = await axios.post('/api/orders', orderData);
      
      if (response.data.success) {
        // Clear cart after successful order
        await clearCart(currentUser);
        setCheckoutDialog(false);
        // Redirect to orders page or show success message
        alert('Order placed successfully!');
      }
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Failed to place order. Please try again.');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            {Array.from({ length: 3 }).map((_, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={3}>
                      <Skeleton variant="rectangular" height={80} />
                    </Grid>
                    <Grid item xs={9}>
                      <Skeleton variant="text" width="60%" height={24} />
                      <Skeleton variant="text" width="40%" height={20} />
                      <Skeleton variant="text" width="30%" height={20} />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={300} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (items.length === 0) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <CartIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Your cart is empty
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Looks like you haven't added any products to your cart yet.
          </Typography>
          <Button
            variant="contained"
            size="large"
            component={RouterLink}
            to="/products"
            startIcon={<ArrowIcon />}
          >
            Start Shopping
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Shopping Cart
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {itemCount} item{itemCount !== 1 ? 's' : ''} in your cart
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Cart Items */}
        <Grid item xs={12} md={8}>
          {items.map((item) => {
            const product = products[item.productId];
            if (!product) return null;

            return (
              <Card key={item.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    {/* Product Image */}
                    <Grid item xs={3} sm={2}>
                      <CardMedia
                        component="img"
                        height="80"
                        image={product.image}
                        alt={product.name}
                        sx={{ objectFit: 'cover', borderRadius: 1 }}
                      />
                    </Grid>

                    {/* Product Info */}
                    <Grid item xs={9} sm={6}>
                      <Typography variant="h6" gutterBottom>
                        {product.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {product.category}
                      </Typography>
                      <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                        ${product.price}
                      </Typography>
                    </Grid>

                    {/* Quantity Controls */}
                    <Grid item xs={6} sm={2}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <IconButton
                          size="small"
                          onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                          disabled={item.quantity <= 1}
                        >
                          <RemoveIcon />
                        </IconButton>
                        <TextField
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value))}
                          inputProps={{ min: 1, max: product.stock }}
                          sx={{ width: 60 }}
                          size="small"
                        />
                        <IconButton
                          size="small"
                          onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                          disabled={item.quantity >= product.stock}
                        >
                          <AddIcon />
                        </IconButton>
                      </Box>
                    </Grid>

                    {/* Total and Actions */}
                    <Grid item xs={6} sm={2}>
                      <Box sx={{ textAlign: 'right' }}>
                        <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                          ${(product.price * item.quantity).toFixed(2)}
                        </Typography>
                        <IconButton
                          color="error"
                          onClick={() => handleRemoveItem(item.id)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            );
          })}

          {/* Cart Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button
              variant="outlined"
              color="error"
              onClick={handleClearCart}
            >
              Clear Cart
            </Button>
            <Button
              variant="outlined"
              component={RouterLink}
              to="/products"
            >
              Continue Shopping
            </Button>
          </Box>
        </Grid>

        {/* Order Summary */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, position: 'sticky', top: 20 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              Order Summary
            </Typography>
            
            <Box sx={{ my: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Subtotal ({itemCount} items)</Typography>
                <Typography>${calculateSubtotal().toFixed(2)}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Tax (8%)</Typography>
                <Typography>${calculateTax().toFixed(2)}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Shipping</Typography>
                <Typography>
                  {calculateShipping() === 0 ? 'Free' : `$${calculateShipping().toFixed(2)}`}
                </Typography>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Total
                </Typography>
                <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                  ${calculateTotal().toFixed(2)}
                </Typography>
              </Box>

              {calculateSubtotal() < 50 && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Add ${(50 - calculateSubtotal()).toFixed(2)} more for free shipping!
                </Alert>
              )}

              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<PaymentIcon />}
                onClick={() => setCheckoutDialog(true)}
                disabled={items.length === 0}
              >
                Proceed to Checkout
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Checkout Dialog */}
      <Dialog
        open={checkoutDialog}
        onClose={() => setCheckoutDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Checkout</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Shipping Address */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Shipping Address
              </Typography>
              <TextField
                fullWidth
                label="Street Address"
                value={checkoutForm.shippingAddress.street}
                onChange={(e) => setCheckoutForm(prev => ({
                  ...prev,
                  shippingAddress: { ...prev.shippingAddress, street: e.target.value }
                }))}
                sx={{ mb: 2 }}
              />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="City"
                    value={checkoutForm.shippingAddress.city}
                    onChange={(e) => setCheckoutForm(prev => ({
                      ...prev,
                      shippingAddress: { ...prev.shippingAddress, city: e.target.value }
                    }))}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="State"
                    value={checkoutForm.shippingAddress.state}
                    onChange={(e) => setCheckoutForm(prev => ({
                      ...prev,
                      shippingAddress: { ...prev.shippingAddress, state: e.target.value }
                    }))}
                  />
                </Grid>
              </Grid>
              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="ZIP Code"
                    value={checkoutForm.shippingAddress.zipCode}
                    onChange={(e) => setCheckoutForm(prev => ({
                      ...prev,
                      shippingAddress: { ...prev.shippingAddress, zipCode: e.target.value }
                    }))}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Country"
                    value={checkoutForm.shippingAddress.country}
                    onChange={(e) => setCheckoutForm(prev => ({
                      ...prev,
                      shippingAddress: { ...prev.shippingAddress, country: e.target.value }
                    }))}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Payment and Notes */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Payment Method
              </Typography>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Payment Method</InputLabel>
                <Select
                  value={checkoutForm.paymentMethod}
                  label="Payment Method"
                  onChange={(e) => setCheckoutForm(prev => ({
                    ...prev,
                    paymentMethod: e.target.value
                  }))}
                >
                  <MenuItem value="credit_card">Credit Card</MenuItem>
                  <MenuItem value="debit_card">Debit Card</MenuItem>
                  <MenuItem value="paypal">PayPal</MenuItem>
                </Select>
              </FormControl>

              <Typography variant="h6" gutterBottom>
                Order Notes
              </Typography>
              <TextareaAutosize
                minRows={3}
                placeholder="Any special instructions or notes for your order..."
                value={checkoutForm.notes}
                onChange={(e) => setCheckoutForm(prev => ({
                  ...prev,
                  notes: e.target.value
                }))}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  fontFamily: 'inherit',
                  fontSize: '14px'
                }}
              />
            </Grid>
          </Grid>

          {/* Order Summary in Dialog */}
          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              Order Summary
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography>Subtotal ({itemCount} items)</Typography>
              <Typography>${calculateSubtotal().toFixed(2)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography>Tax (8%)</Typography>
              <Typography>${calculateTax().toFixed(2)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography>Shipping</Typography>
              <Typography>
                {calculateShipping() === 0 ? 'Free' : `$${calculateShipping().toFixed(2)}`}
              </Typography>
            </Box>
            <Divider sx={{ my: 1 }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Total
              </Typography>
              <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                ${calculateTotal().toFixed(2)}
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCheckoutDialog(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCheckout}
            startIcon={<PaymentIcon />}
          >
            Place Order
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CartPage;
