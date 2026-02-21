import { createSlice } from '@reduxjs/toolkit';

const companySlice = createSlice({
  name: 'company',
  initialState: { currentCompany: null, companies: [] },
  reducers: {
    setCurrentCompany: (state, action) => { state.currentCompany = action.payload; },
    setCompanies: (state, action) => { state.companies = action.payload; },
  },
});

export const { setCurrentCompany, setCompanies } = companySlice.actions;
export default companySlice.reducer;
