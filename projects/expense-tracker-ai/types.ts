
export const expenseCategories = [
  "Food",
  "Transport",
  "Utilities",
  "Entertainment",
  "Shopping",
  "Health",
  "Housing",
  "Other",
] as const;

export type ExpenseCategory = typeof expenseCategories[number];

export interface ExpenseItem {
  name: string;
  price: number;
}

export interface ExpenseData {
  merchant: string;
  date: string; // YYYY-MM-DD format from form
  total: number;
  currency: string;
  category: ExpenseCategory;
  items: ExpenseItem[];
}

export interface Expense extends ExpenseData {
  id: string;
  date: string; // ISO string format for storage
}

export type TimeView = "Daily" | "Weekly" | "Monthly" | "Yearly";
