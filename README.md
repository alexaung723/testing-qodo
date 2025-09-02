# 🛒 Shopping Cart Application

A full-stack e-commerce application built with React (frontend) and Node.js (backend), featuring a modern Material-UI design and comprehensive shopping cart functionality.

## ✨ Features

### Frontend (React + Material-UI)
- **Responsive Design**: Mobile-first approach with Material-UI components
- **Product Catalog**: Browse products with filtering, search, and pagination
- **Shopping Cart**: Add/remove items, quantity management, and checkout
- **User Profile**: Manage personal information and preferences
- **Order History**: Track order status and view detailed order information
- **Modern UI**: Clean, intuitive interface with smooth animations

### Backend (Node.js + Express)
- **RESTful API**: Well-structured endpoints for all operations
- **Product Management**: CRUD operations for products with categories and tags
- **Cart System**: In-memory cart management with user isolation
- **Order Processing**: Complete order lifecycle from creation to delivery
- **User Management**: User profiles, preferences, and authentication ready
- **Security**: Rate limiting, CORS, and input validation

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Backend Setup
```bash
cd backend
npm install
npm run dev
```

The backend will start on `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The frontend will start on `http://localhost:3000`

## 📁 Project Structure

```
├── backend/                 # Node.js backend
│   ├── routes/             # API route handlers
│   │   ├── products.js     # Product management
│   │   ├── cart.js         # Shopping cart operations
│   │   ├── orders.js       # Order processing
│   │   └── users.js        # User management
│   ├── server.js           # Express server setup
│   ├── package.json        # Backend dependencies
│   └── env.example         # Environment variables template
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── Header.js   # Navigation header
│   │   │   └── Footer.js   # Page footer
│   │   ├── contexts/       # React contexts
│   │   │   └── CartContext.js # Shopping cart state management
│   │   ├── pages/          # Page components
│   │   │   ├── HomePage.js      # Landing page
│   │   │   ├── ProductsPage.js  # Product catalog
│   │   │   ├── ProductDetailPage.js # Individual product view
│   │   │   ├── CartPage.js      # Shopping cart
│   │   │   ├── OrdersPage.js    # Order history
│   │   │   └── ProfilePage.js   # User profile
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Application entry point
│   └── package.json        # Frontend dependencies
│
└── README.md               # This file
```

## 🔌 API Endpoints

### Products
- `GET /api/products` - Get all products with filtering
- `GET /api/products/:id` - Get product by ID
- `GET /api/products/categories/list` - Get all categories
- `GET /api/products/featured/list` - Get featured products

### Cart
- `GET /api/cart/:userId` - Get user's cart
- `POST /api/cart/:userId/items` - Add item to cart
- `PUT /api/cart/:userId/items/:itemId` - Update item quantity
- `DELETE /api/cart/:userId/items/:itemId` - Remove item from cart
- `DELETE /api/cart/:userId` - Clear entire cart

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/user/:userId` - Get user's orders
- `GET /api/orders/:orderId` - Get order by ID
- `PATCH /api/orders/:orderId/status` - Update order status
- `PATCH /api/orders/:orderId/cancel` - Cancel order

### Users
- `GET /api/users` - Get all users (admin)
- `GET /api/users/:userId` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/:userId` - Update user
- `DELETE /api/users/:userId` - Delete user

## 🎨 UI Components

### Material-UI Integration
- **Theme**: Custom theme with consistent color palette and typography
- **Components**: Cards, Buttons, Forms, Tables, and more
- **Responsive**: Grid system for mobile and desktop layouts
- **Icons**: Material Design icons throughout the interface

### Key Features
- **Product Cards**: Attractive product display with images and details
- **Shopping Cart**: Real-time cart updates with quantity controls
- **Checkout Flow**: Multi-step checkout with form validation
- **Order Tracking**: Visual order status with timeline
- **User Profile**: Editable profile with preference management

## 🛠️ Development

### Backend Development
```bash
cd backend
npm run dev          # Start with nodemon for development
npm start           # Start production server
```

### Frontend Development
```bash
cd frontend
npm start           # Start development server
npm run build      # Build for production
npm test           # Run tests
```

### Environment Variables
Create a `.env` file in the backend directory:
```env
PORT=5000
NODE_ENV=development
FRONTEND_URL=http://localhost:3000
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=24h
```

## 🔒 Security Features

- **Rate Limiting**: API request throttling
- **CORS**: Cross-origin resource sharing configuration
- **Input Validation**: Request data validation and sanitization
- **Error Handling**: Comprehensive error handling and logging
- **Security Headers**: Helmet.js for security headers

## 📱 Responsive Design

- **Mobile First**: Optimized for mobile devices
- **Breakpoints**: Responsive grid system with Material-UI breakpoints
- **Touch Friendly**: Optimized for touch interactions
- **Progressive Enhancement**: Works on all device sizes

## 🚀 Deployment

### Backend Deployment
```bash
cd backend
npm install --production
npm start
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy the build/ folder to your hosting service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the code examples

## 🔮 Future Enhancements

- [ ] User authentication and authorization
- [ ] Payment gateway integration
- [ ] Real-time inventory management
- [ ] Advanced search and filtering
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Multi-language support

---

**Happy Shopping! 🛒✨**
