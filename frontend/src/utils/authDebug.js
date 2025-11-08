import { useAuthStore } from '../store/authStore';

// Debug утилита для проверки авторизации
export const debugAuth = () => {
  const state = useAuthStore.getState();
  
  console.log('=== Auth Debug Info ===');
  console.log('Is Authenticated:', state.isAuthenticated);
  console.log('User:', state.user);
  console.log('Token exists:', !!state.token);
  console.log('Token preview:', state.token ? state.token.substring(0, 20) + '...' : 'No token');
  console.log('Refresh Token exists:', !!state.refreshToken);
  console.log('======================');
  
  // Проверка localStorage
  const storedData = localStorage.getItem('auth-storage');
  if (storedData) {
    try {
      const parsed = JSON.parse(storedData);
      console.log('LocalStorage auth data:', {
        hasToken: !!parsed.state?.token,
        hasUser: !!parsed.state?.user,
        isAuth: parsed.state?.isAuthenticated
      });
    } catch (e) {
      console.error('Error parsing auth storage:', e);
    }
  } else {
    console.log('No auth data in localStorage');
  }
  
  return state;
};

// Функция для проверки валидности токена
export const checkTokenValidity = async () => {
  const state = useAuthStore.getState();
  
  if (!state.token) {
    console.error('No token found');
    return false;
  }
  
  try {
    // Попытка декодировать JWT
    const tokenParts = state.token.split('.');
    if (tokenParts.length !== 3) {
      console.error('Invalid token format');
      return false;
    }
    
    const payload = JSON.parse(atob(tokenParts[1]));
    console.log('Token payload:', payload);
    
    // Проверка срока действия
    const exp = payload.exp;
    const now = Math.floor(Date.now() / 1000);
    
    if (exp < now) {
      console.error('Token expired:', new Date(exp * 1000));
      return false;
    }
    
    console.log('Token valid until:', new Date(exp * 1000));
    return true;
    
  } catch (e) {
    console.error('Error checking token:', e);
    return false;
  }
};
