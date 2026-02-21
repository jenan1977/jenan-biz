import { createSlice } from '@reduxjs/toolkit';

const settingsSlice = createSlice({
  name: 'settings',
  initialState: { theme: 'light', language: 'ar', currency: 'SAR' },
  reducers: {
    setTheme: (state, action) => { state.theme = action.payload; },
    setLanguage: (state, action) => { state.language = action.payload; },
    setCurrency: (state, action) => { state.currency = action.payload; },
  },
});

export const { setTheme, setLanguage, setCurrency } = settingsSlice.actions;
export default settingsSlice.reducer;
