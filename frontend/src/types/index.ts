export interface User { id: number; username: string; email: string; full_name: string; is_admin: boolean; }
export interface Product { id: number; name: string; description?: string; sku: string; cost_price: number; selling_price: number; stock_quantity: number; min_stock_level: number; image_url?: string; category?: string; unit: string; is_active: boolean; }
export interface Supplier { id: number; name: string; contact_person?: string; phone?: string; email?: string; address?: string; tax_number?: string; is_active: boolean; }
export interface Customer { id: number; name: string; contact_person?: string; phone?: string; email?: string; address?: string; tax_number?: string; is_active: boolean; }
export interface PurchaseItem { id?: number; product_id: number; product_name?: string; quantity: number; unit_price: number; total_price: number; }
export interface PurchaseInvoice { id: number; invoice_number: string; supplier_id: number; supplier_name?: string; date: string; subtotal: number; tax_amount: number; total_amount: number; apply_tax: boolean; notes?: string; file_url?: string; status: string; items: PurchaseItem[]; }
export interface SaleItem { id?: number; product_id: number; product_name?: string; quantity: number; unit_price: number; cost_price?: number; total_price: number; }
export interface SaleInvoice { id: number; invoice_number: string; customer_id: number; customer_name?: string; date: string; subtotal: number; tax_amount: number; total_amount: number; apply_tax: boolean; profit: number; notes?: string; status: string; items: SaleItem[]; }
export interface StockMovement { id: number; product_id: number; product_name?: string; movement_type: string; quantity: number; reference_id?: number; notes?: string; created_at: string; }
export interface DashboardSummary { today_sales: number; today_purchases: number; total_products: number; low_stock_count: number; today_sales_count: number; today_purchases_count: number; recent_transactions: any[]; }
