
import React, { useState } from 'react';
import { useLocalStorage } from './hooks/useLocalStorage';
import { Expense, ExpenseData } from './types';
import Dashboard from './components/Dashboard';
import ReceiptProcessorModal from './components/ReceiptProcessorModal';
import { PlusIcon } from './components/icons/Icons';
import ExpenseList from './components/ExpenseList';

const App: React.FC = () => {
  const [expenses, setExpenses] = useLocalStorage<Expense[]>('expenses', []);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAddExpense = (expenseData: ExpenseData) => {
    const newExpense: Expense = {
      ...expenseData,
      id: `${Date.now()}-${Math.random()}`,
      date: new Date(expenseData.date).toISOString(), // Ensure date is ISO string
    };
    setExpenses(prevExpenses => [...prevExpenses, newExpense].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()));
    setIsModalOpen(false);
  };

  const handleDeleteExpense = (id: string) => {
    setExpenses(prevExpenses => prevExpenses.filter(expense => expense.id !== id));
  }

  return (
    <div className="min-h-screen bg-base-100 font-sans">
      <header className="bg-base-200/50 backdrop-blur-sm sticky top-0 z-20 shadow-lg">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Expense Tracker <span className="text-brand-primary">AI</span>
            </h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 bg-brand-primary hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-transform transform hover:scale-105"
            >
              <PlusIcon className="w-5 h-5" />
              <span>Add Expense</span>
            </button>
          </div>
        </div>
      </header>
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <Dashboard expenses={expenses} />
        <ExpenseList expenses={expenses.slice(0, 10)} onDelete={handleDeleteExpense} />
      </main>
      <ReceiptProcessorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleAddExpense}
      />
    </div>
  );
};

export default App;
