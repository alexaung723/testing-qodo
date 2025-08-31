import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import ProductsPage from './pages/ProductsPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import ProfilePage from './pages/ProfilePage';
import { CartProvider } from './contexts/CartContext';

function App() {
  const [currentUser] = useState('demo-user-1'); // Demo user for now

  return (
    <CartProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header currentUser={currentUser} />
        
        <Container component="main" sx={{ flex: 1, py: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:productId" element={<ProductDetailPage />} />
            <Route path="/cart" element={<CartPage currentUser={currentUser} />} />
            <Route path="/orders" element={<OrdersPage currentUser={currentUser} />} />
            <Route path="/profile" element={<ProfilePage currentUser={currentUser} />} />
          </Routes>
        </Container>
        
        <Footer />
      </Box>
    </CartProvider>
  );
}

export default App;
