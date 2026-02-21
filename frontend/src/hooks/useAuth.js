import { useSelector, useDispatch } from 'react-redux';
import { useCallback } from 'react';
import { logout, setCredentials } from '../store/authSlice';
import { authService } from '../services/authService';

export function useAuth() {
  const dispatch = useDispatch();
  const { user, token, isAuthenticated } = useSelector((state) => state.auth);

  const login = useCallback(async (email, password) => {
    const response = await authService.login(email, password);
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    const meResponse = await authService.getMe();
    dispatch(setCredentials({ user: meResponse.data, token: access_token }));
    return meResponse.data;
  }, [dispatch]);

  const logoutUser = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    dispatch(logout());
  }, [dispatch]);

  return { user, token, isAuthenticated, login, logout: logoutUser };
}
