import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import store from './store';
import { useSelector } from 'react-redux';
import './styles/global.css';
import './styles/responsive.css';

import Navbar from './components/Common/Navbar';
import Sidebar from './components/Common/Sidebar';

// Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import BusinessSetup from './pages/Setup/BusinessSetup';
import Dashboard from './pages/Dashboard/Dashboard';
import ProductsList from './pages/Products/ProductsList';
import CategoriesManager from './pages/Products/CategoriesManager';
import InvoiceList from './pages/Sales/InvoiceList';
import InvoiceForm from './pages/Sales/InvoiceForm';
import PurchaseList from './pages/Purchases/PurchaseList';
import PurchaseForm from './pages/Purchases/PurchaseForm';
import InventoryList from './pages/Inventory/InventoryList';
import StockMovements from './pages/Inventory/StockMovements';
import CustomersList from './pages/Customers/CustomersList';
import SuppliersList from './pages/Suppliers/SuppliersList';
import SalesReport from './pages/Reports/SalesReport';
import ProfitReport from './pages/Reports/ProfitReport';
import PurchaseReport from './pages/Reports/PurchaseReport';
import TaxReport from './pages/Reports/TaxReport';
import Heatmap from './pages/Analytics/Heatmap';
import TopProducts from './pages/Analytics/TopProducts';
import CompanySettings from './pages/Settings/CompanySettings';
import UserSettings from './pages/Settings/UserSettings';

function ProtectedRoute({ children }) {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  return (
    <>
      <Navbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar isOpen={sidebarOpen} />
      <main className={`main-content`} style={{
        marginRight: sidebarOpen ? 'var(--sidebar-width)' : '0',
        marginTop: 'var(--navbar-height)',
        padding: '1.5rem',
        transition: 'margin-right 0.3s ease',
      }}>
        {children}
      </main>
    </>
  );
}

function AppRoutes() {
  const { theme } = useSelector((state) => state.settings);
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/setup" element={<ProtectedRoute><BusinessSetup /></ProtectedRoute>} />
        <Route path="/*" element={
          <ProtectedRoute>
            <AppLayout>
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/products" element={<ProductsList />} />
                <Route path="/products/categories" element={<CategoriesManager />} />
                <Route path="/sales" element={<InvoiceList />} />
                <Route path="/sales/new" element={<InvoiceForm />} />
                <Route path="/purchases" element={<PurchaseList />} />
                <Route path="/purchases/new" element={<PurchaseForm />} />
                <Route path="/inventory" element={<InventoryList />} />
                <Route path="/inventory/movements" element={<StockMovements />} />
                <Route path="/customers" element={<CustomersList />} />
                <Route path="/suppliers" element={<SuppliersList />} />
                <Route path="/reports/sales" element={<SalesReport />} />
                <Route path="/reports/purchases" element={<PurchaseReport />} />
                <Route path="/reports/profit" element={<ProfitReport />} />
                <Route path="/reports/tax" element={<TaxReport />} />
                <Route path="/analytics" element={<Heatmap />} />
                <Route path="/analytics/top-products" element={<TopProducts />} />
                <Route path="/settings" element={<CompanySettings />} />
                <Route path="/settings/user" element={<UserSettings />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </AppLayout>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <AppRoutes />
      <ToastContainer position="top-right" rtl />
    </Provider>
  );
}
