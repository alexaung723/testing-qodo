import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

const CartContext = createContext();

const cartReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CART':
      return {
        ...state,
        items: action.payload.items || [],
        total: action.payload.total || 0,
        itemCount: action.payload.itemCount || 0,
        loading: false
      };
    
    case 'ADD_ITEM':
      const existingItemIndex = state.items.findIndex(item => item.productId === action.payload.productId);
      
      if (existingItemIndex >= 0) {
        const updatedItems = [...state.items];
        updatedItems[existingItemIndex].quantity += action.payload.quantity;
        return {
          ...state,
          items: updatedItems,
          itemCount: state.itemCount + action.payload.quantity,
          loading: false
        };
      } else {
        return {
          ...state,
          items: [...state.items, action.payload],
          itemCount: state.itemCount + action.payload.quantity,
          loading: false
        };
      }
    
    case 'UPDATE_ITEM_QUANTITY':
      const updatedItems = state.items.map(item => 
        item.id === action.payload.itemId 
          ? { ...item, quantity: action.payload.quantity }
          : item
      );
      
      const newItemCount = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
      
      return {
        ...state,
        items: updatedItems,
        itemCount: newItemCount,
        loading: false
      };
    
    case 'REMOVE_ITEM':
      const itemToRemove = state.items.find(item => item.id === action.payload);
      const remainingItems = state.items.filter(item => item.id !== action.payload);
      
      return {
        ...state,
        items: remainingItems,
        itemCount: state.itemCount - (itemToRemove?.quantity || 0),
        loading: false
      };
    
    case 'CLEAR_CART':
      return {
        ...state,
        items: [],
        total: 0,
        itemCount: 0,
        loading: false
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    
    default:
      return state;
  }
};

export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, {
    items: [],
    total: 0,
    itemCount: 0,
    loading: false,
    error: null
  });

  const fetchCart = async (userId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.get(`/api/cart/${userId}`);
      
      if (response.data.success) {
        dispatch({ type: 'SET_CART', payload: response.data.data });
      }
    } catch (error) {
      console.error('Error fetching cart:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch cart' });
    }
  };

  const addToCart = async (userId, productId, quantity = 1) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.post(`/api/cart/${userId}/items`, {
        productId,
        quantity
      });
      
      if (response.data.success) {
        dispatch({ type: 'ADD_ITEM', payload: { productId, quantity } });
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to add item to cart' });
    }
  };

  const updateItemQuantity = async (userId, itemId, quantity) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.put(`/api/cart/${userId}/items/${itemId}`, {
        quantity
      });
      
      if (response.data.success) {
        dispatch({ type: 'UPDATE_ITEM_QUANTITY', payload: { itemId, quantity } });
      }
    } catch (error) {
      console.error('Error updating item quantity:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to update item quantity' });
    }
  };

  const removeFromCart = async (userId, itemId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.delete(`/api/cart/${userId}/items/${itemId}`);
      
      if (response.data.success) {
        dispatch({ type: 'REMOVE_ITEM', payload: itemId });
      }
    } catch (error) {
      console.error('Error removing item:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to remove item from cart' });
    }
  };

  const clearCart = async (userId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.delete(`/api/cart/${userId}`);
      
      if (response.data.success) {
        dispatch({ type: 'CLEAR_CART' });
      }
    } catch (error) {
      console.error('Error clearing cart:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to clear cart' });
    }
  };

  const value = {
    ...state,
    fetchCart,
    addToCart,
    updateItemQuantity,
    removeFromCart,
    clearCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
