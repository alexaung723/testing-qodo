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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Rating,
  Skeleton,
  Alert,
  Pagination,
  InputAdornment,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  ShoppingCart as CartIcon,
  ArrowForward as ArrowIcon,
  ExpandMore as ExpandIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    minPrice: '',
    maxPrice: '',
    sortBy: ''
  });
  const [priceRange, setPriceRange] = useState([0, 500]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const { addToCart } = useCart();

  const productsPerPage = 12;

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/products/categories/list');
        if (response.data.success) {
          setCategories(response.data.data);
        }
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const params = {
          ...filters,
          limit: productsPerPage,
          offset: (currentPage - 1) * productsPerPage
        };
        
        const response = await axios.get('/api/products', { params });
        if (response.data.success) {
          setProducts(response.data.data);
          setTotalProducts(response.data.total);
        }
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('Failed to load products');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [filters, currentPage]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handlePriceRangeChange = (event, newValue) => {
    setPriceRange(newValue);
    setFilters(prev => ({
      ...prev,
      minPrice: newValue[0],
      maxPrice: newValue[1]
    }));
    setCurrentPage(1);
  };

  const handleAddToCart = async (productId) => {
    try {
      await addToCart('demo-user-1', productId, 1);
    } catch (err) {
      console.error('Error adding to cart:', err);
    }
  };

  const handlePageChange = (event, value) => {
    setCurrentPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const totalPages = Math.ceil(totalProducts / productsPerPage);

  const ProductCard = ({ product }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardMedia
        component="img"
        height="200"
        image={product.image}
        alt={product.name}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="h3" noWrap>
          {product.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {product.description}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Rating value={product.rating} precision={0.1} size="small" readOnly />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            ({product.reviews})
          </Typography>
        </Box>
        <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
          ${product.price}
        </Typography>
        <Chip 
          label={product.category} 
          size="small" 
          sx={{ mt: 1 }}
          color="primary"
          variant="outlined"
        />
      </CardContent>
      <CardActions>
        <Button
          size="small"
          startIcon={<CartIcon />}
          onClick={() => handleAddToCart(product.id)}
          fullWidth
        >
          Add to Cart
        </Button>
        <Button
          size="small"
          component={RouterLink}
          to={`/products/${product.id}`}
          endIcon={<ArrowIcon />}
          fullWidth
        >
          View Details
        </Button>
      </CardActions>
    </Card>
  );

  const ProductSkeleton = () => (
    <Card sx={{ height: '100%' }}>
      <Skeleton variant="rectangular" height={200} />
      <CardContent>
        <Skeleton variant="text" height={32} />
        <Skeleton variant="text" height={20} />
        <Skeleton variant="text" height={20} />
        <Skeleton variant="text" height={24} />
        <Skeleton variant="text" height={20} />
      </CardContent>
      <CardActions>
        <Skeleton variant="rectangular" height={36} width="100%" />
      </CardActions>
    </Card>
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          All Products
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover our complete collection of amazing products
        </Typography>
      </Box>

      {/* Filters Section */}
      <Accordion defaultExpanded sx={{ mb: 4 }}>
        <AccordionSummary expandIcon={<ExpandIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterIcon />
            <Typography variant="h6">Filters & Search</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            {/* Search */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search products"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                placeholder="Search by name, description, or tags..."
              />
            </Grid>

            {/* Category Filter */}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={filters.category}
                  label="Category"
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Sort By */}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Sort By</InputLabel>
                <Select
                  value={filters.sortBy}
                  label="Sort By"
                  onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                >
                  <MenuItem value="">Default</MenuItem>
                  <MenuItem value="price-low">Price: Low to High</MenuItem>
                  <MenuItem value="price-high">Price: High to Low</MenuItem>
                  <MenuItem value="rating">Highest Rated</MenuItem>
                  <MenuItem value="reviews">Most Reviewed</MenuItem>
                  <MenuItem value="name">Name: A to Z</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Price Range */}
            <Grid item xs={12}>
              <Typography gutterBottom>Price Range</Typography>
              <Slider
                value={priceRange}
                onChange={handlePriceRangeChange}
                valueLabelDisplay="auto"
                min={0}
                max={500}
                step={10}
                marks={[
                  { value: 0, label: '$0' },
                  { value: 100, label: '$100' },
                  { value: 250, label: '$250' },
                  { value: 500, label: '$500' }
                ]}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  ${priceRange[0]}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ${priceRange[1]}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Products Grid */}
      <Grid container spacing={3}>
        {loading
          ? Array.from({ length: productsPerPage }).map((_, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                <ProductSkeleton />
              </Grid>
            ))
          : products.map((product) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                <ProductCard product={product} />
              </Grid>
            ))}
      </Grid>

      {!loading && products.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No products found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your filters or search terms
          </Typography>
        </Box>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={handlePageChange}
            color="primary"
            size="large"
          />
        </Box>
      )}

      {/* Results Summary */}
      {!loading && (
        <Box sx={{ textAlign: 'center', mt: 4, mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Showing {products.length} of {totalProducts} products
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default ProductsPage;
