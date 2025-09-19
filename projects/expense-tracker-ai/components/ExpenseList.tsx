
import React from 'react';
import { Expense } from '../types';
import { getCurrencySymbol } from '../utils/dataProcessor';
import { format } from 'date-fns';
import { TrashIcon } from './icons/Icons';

interface ExpenseListProps {
  expenses: Expense[];
  onDelete: (id: string) => void;
}

const CategoryBadge: React.FC<{ category: string }> = ({ category }) => {
  const colors: { [key: string]: string } = {
    Food: 'bg-blue-500/20 text-blue-300',
    Transport: 'bg-yellow-500/20 text-yellow-300',
    Utilities: 'bg-purple-500/20 text-purple-300',
    Entertainment: 'bg-pink-500/20 text-pink-300',
    Shopping: 'bg-green-500/20 text-green-300',
    Health: 'bg-red-500/20 text-red-300',
    Housing: 'bg-indigo-500/20 text-indigo-300',
    Other: 'bg-gray-500/20 text-gray-300',
  };
  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[category] || colors['Other']}`}>
      {category}
    </span>
  );
};


const ExpenseList: React.FC<ExpenseListProps> = ({ expenses, onDelete }) => {
  if (expenses.length === 0) {
    return (
        <div className="mt-8 bg-base-200 p-8 rounded-xl shadow-lg text-center">
            <h3 className="text-xl font-bold text-white mb-2">No expenses yet!</h3>
            <p className="text-gray-400">Click "Add Expense" to get started.</p>
        </div>
    );
  }
  
  return (
    <div className="mt-8 bg-base-200 p-4 sm:p-6 rounded-xl shadow-lg">
      <h3 className="text-xl font-bold text-white mb-4">Recent Expenses</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="border-b border-base-300 text-sm text-gray-400">
            <tr>
              <th className="p-3">Merchant</th>
              <th className="p-3 hidden sm:table-cell">Date</th>
              <th className="p-3">Category</th>
              <th className="p-3 text-right">Amount</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {expenses.map(expense => (
              <tr key={expense.id} className="border-b border-base-300 hover:bg-base-300/50">
                <td className="p-3 font-medium text-white">{expense.merchant}</td>
                <td className="p-3 text-gray-400 hidden sm:table-cell">{format(new Date(expense.date), 'MMM d, yyyy')}</td>
                <td className="p-3">
                  <CategoryBadge category={expense.category} />
                </td>
                <td className="p-3 font-mono text-right text-white">
                  {getCurrencySymbol(expense.currency)}{expense.total.toFixed(2)}
                </td>
                <td className="p-3 text-right">
                    <button onClick={() => onDelete(expense.id)} className="text-gray-500 hover:text-red-500 transition-colors p-1">
                        <TrashIcon className="w-4 h-4" />
                    </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExpenseList;
