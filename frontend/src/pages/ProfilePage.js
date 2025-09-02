import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Avatar,
  Divider,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Skeleton,
  Paper,
  Chip
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import axios from 'axios';

const ProfilePage = ({ currentUser }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    address: {
      street: '',
      city: '',
      state: '',
      zipCode: '',
      country: ''
    },
    preferences: {
      newsletter: false,
      marketing: false,
      language: 'en',
      currency: 'USD'
    }
  });

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/users/${currentUser}`);
        if (response.data.success) {
          const userData = response.data.data;
          setUser(userData);
          setFormData({
            firstName: userData.firstName || '',
            lastName: userData.lastName || '',
            email: userData.email || '',
            phone: userData.phone || '',
            address: userData.address || {
              street: '',
              city: '',
              state: '',
              zipCode: '',
              country: ''
            },
            preferences: userData.preferences || {
              newsletter: false,
              marketing: false,
              language: 'en',
              currency: 'USD'
            }
          });
        }
      } catch (err) {
        console.error('Error fetching user:', err);
        setError('Failed to load user profile');
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchUser();
    }
  }, [currentUser]);

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleSave = async () => {
    try {
      setSaveLoading(true);
      const response = await axios.put(`/api/users/${currentUser}`, formData);
      
      if (response.data.success) {
        setUser(response.data.data);
        setEditMode(false);
        setSuccessMessage('Profile updated successfully!');
        setTimeout(() => setSuccessMessage(''), 3000);
      }
    } catch (err) {
      console.error('Error updating user:', err);
      setError('Failed to update profile');
    } finally {
      setSaveLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset form data to original user data
    if (user) {
      setFormData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.email || '',
        phone: user.phone || '',
        address: user.address || {
          street: '',
          city: '',
          state: '',
          zipCode: '',
          country: ''
        },
        preferences: user.preferences || {
          newsletter: false,
          marketing: false,
          language: 'en',
          currency: 'USD'
        }
      });
    }
    setEditMode(false);
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={200} />
          </Grid>
          <Grid item xs={12} md={8}>
            <Skeleton variant="text" width="60%" height={32} />
            <Skeleton variant="text" width="40%" height={24} />
            <Skeleton variant="text" width="80%" height={24} />
            <Skeleton variant="text" width="70%" height={24} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (error || !user) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || 'User not found'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your account settings and preferences
        </Typography>
      </Box>

      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {successMessage}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Profile Header */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item>
                  <Avatar
                    sx={{ 
                      width: 80, 
                      height: 80, 
                      bgcolor: 'primary.main',
                      fontSize: '2rem'
                    }}
                  >
                    {user.firstName?.charAt(0)}{user.lastName?.charAt(0)}
                  </Avatar>
                </Grid>
                <Grid item xs>
                  <Typography variant="h4" gutterBottom>
                    {user.firstName} {user.lastName}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    Member since {new Date(user.createdAt).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long'
                    })}
                  </Typography>
                  <Chip label={`User ID: ${user.id}`} variant="outlined" size="small" />
                </Grid>
                <Grid item>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    {editMode ? (
                      <>
                        <Button
                          variant="outlined"
                          onClick={handleCancel}
                          disabled={saveLoading}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="contained"
                          onClick={handleSave}
                          disabled={saveLoading}
                        >
                          {saveLoading ? 'Saving...' : 'Save Changes'}
                        </Button>
                      </>
                    ) : (
                      <Button
                        variant="contained"
                        startIcon={<SettingsIcon />}
                        onClick={() => setEditMode(true)}
                      >
                        Edit Profile
                      </Button>
                    )}
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Information */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon />
                Personal Information
              </Typography>
              
              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange('firstName', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    disabled={!editMode}
                    type="email"
                    InputProps={{
                      startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Phone"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    disabled={!editMode}
                    InputProps={{
                      startAdornment: <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Address Information */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationIcon />
                Address Information
              </Typography>
              
              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Street Address"
                    value={formData.address.street}
                    onChange={(e) => handleInputChange('address.street', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="City"
                    value={formData.address.city}
                    onChange={(e) => handleInputChange('address.city', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="State"
                    value={formData.address.state}
                    onChange={(e) => handleInputChange('address.state', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="ZIP Code"
                    value={formData.address.zipCode}
                    onChange={(e) => handleInputChange('address.zipCode', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Country"
                    value={formData.address.country}
                    onChange={(e) => handleInputChange('address.country', e.target.value)}
                    disabled={!editMode}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Preferences and Settings */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <NotificationsIcon />
                Preferences
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.preferences.newsletter}
                      onChange={(e) => handleInputChange('preferences.newsletter', e.target.checked)}
                      disabled={!editMode}
                    />
                  }
                  label="Newsletter Subscription"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.preferences.marketing}
                      onChange={(e) => handleInputChange('preferences.marketing', e.target.checked)}
                      disabled={!editMode}
                    />
                  }
                  label="Marketing Communications"
                />
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Language & Currency
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Language</InputLabel>
                <Select
                  value={formData.preferences.language}
                  label="Language"
                  onChange={(e) => handleInputChange('preferences.language', e.target.value)}
                  disabled={!editMode}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                  <MenuItem value="de">German</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={formData.preferences.currency}
                  label="Currency"
                  onChange={(e) => handleInputChange('preferences.currency', e.target.value)}
                  disabled={!editMode}
                >
                  <MenuItem value="USD">USD ($)</MenuItem>
                  <MenuItem value="EUR">EUR (€)</MenuItem>
                  <MenuItem value="GBP">GBP (£)</MenuItem>
                  <MenuItem value="CAD">CAD (C$)</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>

          {/* Account Security */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SecurityIcon />
                Security
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Change Password
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Enable Two-Factor Authentication
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  color="error"
                >
                  Delete Account
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ProfilePage;
