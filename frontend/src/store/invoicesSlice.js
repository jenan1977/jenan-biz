import { createSlice } from '@reduxjs/toolkit';

const invoicesSlice = createSlice({
  name: 'invoices',
  initialState: { items: [], loading: false, error: null },
  reducers: {
    setInvoices: (state, action) => { state.items = action.payload; },
    addInvoice: (state, action) => { state.items.unshift(action.payload); },
    updateInvoice: (state, action) => {
      const idx = state.items.findIndex((i) => i.id === action.payload.id);
      if (idx !== -1) state.items[idx] = action.payload;
    },
    setLoading: (state, action) => { state.loading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
  },
});

export const { setInvoices, addInvoice, updateInvoice, setLoading, setError } = invoicesSlice.actions;
export default invoicesSlice.reducer;
