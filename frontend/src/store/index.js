import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import companyReducer from './companySlice';
import productsReducer from './productsSlice';
import invoicesReducer from './invoicesSlice';
import settingsReducer from './settingsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    company: companyReducer,
    products: productsReducer,
    invoices: invoicesReducer,
    settings: settingsReducer,
  },
});

export default store;
