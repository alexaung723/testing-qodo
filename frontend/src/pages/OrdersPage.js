import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Skeleton,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  Receipt as ReceiptIcon,
  LocalShipping as ShippingIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import axios from 'axios';

const OrdersPage = ({ currentUser }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/orders/user/${currentUser}`);
        if (response.data.success) {
          setOrders(response.data.data);
        }
      } catch (err) {
        console.error('Error fetching orders:', err);
        setError('Failed to load orders');
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchOrders();
    }
  }, [currentUser]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'confirmed':
        return 'info';
      case 'processing':
        return 'primary';
      case 'shipped':
        return 'secondary';
      case 'delivered':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ScheduleIcon />;
      case 'confirmed':
        return <ReceiptIcon />;
      case 'processing':
        return <ReceiptIcon />;
      case 'shipped':
        return <ShippingIcon />;
      case 'delivered':
        return <CheckIcon />;
      case 'cancelled':
        return <CancelIcon />;
      default:
        return <ReceiptIcon />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    return `$${parseFloat(amount).toFixed(2)}`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        {Array.from({ length: 3 }).map((_, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Skeleton variant="text" width="60%" height={24} />
              <Skeleton variant="text" width="40%" height={20} />
              <Skeleton variant="text" width="30%" height={20} />
            </CardContent>
          </Card>
        ))}
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (orders.length === 0) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <ReceiptIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            No orders yet
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            You haven't placed any orders yet. Start shopping to see your order history here.
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Order History
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track your orders and view order details
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {orders.map((order) => (
          <Grid item xs={12} key={order.id}>
            <Card>
              <CardContent>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandIcon />}>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} sm={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(order.status)}
                          <Typography variant="h6" component="span">
                            Order #{order.id.slice(0, 8)}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Placed: {formatDate(order.createdAt)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={2}>
                        <Chip
                          label={order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                          color={getStatusColor(order.status)}
                          variant="outlined"
                        />
                      </Grid>
                      <Grid item xs={12} sm={2}>
                        <Typography variant="body2" color="text.secondary">
                          {order.items.length} item{order.items.length !== 1 ? 's' : ''}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={2}>
                        <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                          {formatCurrency(order.total)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={3}>
                      {/* Order Items */}
                      <Grid item xs={12} md={8}>
                        <Typography variant="h6" gutterBottom>
                          Order Items
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Product</TableCell>
                                <TableCell align="right">Price</TableCell>
                                <TableCell align="right">Quantity</TableCell>
                                <TableCell align="right">Total</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {order.items.map((item) => (
                                <TableRow key={item.id}>
                                  <TableCell>
                                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                      {item.name}
                                    </Typography>
                                  </TableCell>
                                  <TableCell align="right">
                                    {formatCurrency(item.price)}
                                  </TableCell>
                                  <TableCell align="right">
                                    {item.quantity}
                                  </TableCell>
                                  <TableCell align="right">
                                    {formatCurrency(item.price * item.quantity)}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>

                      {/* Order Summary */}
                      <Grid item xs={12} md={4}>
                        <Typography variant="h6" gutterBottom>
                          Order Summary
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Box sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Subtotal:</Typography>
                              <Typography variant="body2">{formatCurrency(order.subtotal)}</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Tax (8%):</Typography>
                              <Typography variant="body2">{formatCurrency(order.tax)}</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                              <Typography variant="body2">Shipping:</Typography>
                              <Typography variant="body2">
                                {order.shipping === 0 ? 'Free' : formatCurrency(order.shipping)}
                              </Typography>
                            </Box>
                            <Divider sx={{ my: 1 }} />
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                Total:
                              </Typography>
                              <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                                {formatCurrency(order.total)}
                              </Typography>
                            </Box>
                          </Box>
                        </Paper>

                        {/* Shipping Information */}
                        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                          Shipping Information
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            <strong>Address:</strong>
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {order.shippingAddress.street}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {order.shippingAddress.city}, {order.shippingAddress.state} {order.shippingAddress.zipCode}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {order.shippingAddress.country}
                          </Typography>
                          
                          <Typography variant="body2" gutterBottom>
                            <strong>Payment Method:</strong> {order.paymentMethod.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Typography>
                          
                          {order.estimatedDelivery && (
                            <Typography variant="body2" gutterBottom sx={{ mt: 1 }}>
                              <strong>Estimated Delivery:</strong> {formatDate(order.estimatedDelivery)}
                            </Typography>
                          )}
                        </Paper>

                        {/* Order Timeline */}
                        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                          Order Timeline
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              <strong>Order Placed:</strong> {formatDate(order.createdAt)}
                            </Typography>
                          </Box>
                          {order.updatedAt !== order.createdAt && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="body2" color="text.secondary">
                                <strong>Last Updated:</strong> {formatDate(order.updatedAt)}
                              </Typography>
                            </Box>
                          )}
                          {order.cancellationReason && (
                            <Box>
                              <Typography variant="body2" color="error">
                                <strong>Cancellation Reason:</strong> {order.cancellationReason}
                              </Typography>
                            </Box>
                          )}
                        </Paper>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default OrdersPage;
