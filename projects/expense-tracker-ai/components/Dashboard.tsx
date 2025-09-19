import React, { useState, useMemo, useEffect } from 'react';
import { Expense, TimeView } from '../types';
import { processExpensesForCharts, getCurrencySymbol, getDisplayDateRange } from '../utils/dataProcessor';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, LineChart, Line } from 'recharts';
import { addDays, subDays, addWeeks, subWeeks, addMonths, subMonths, addYears, subYears } from 'date-fns';
import { ChevronLeftIcon, ChevronRightIcon } from './icons/Icons';


interface DashboardProps {
  expenses: Expense[];
}

const COLORS = ['#4f46e5', '#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#64748b'];

const CustomTooltip = ({ active, payload, label, currencySymbol }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-base-300 p-2 border border-gray-500 rounded-lg shadow-lg">
        <p className="label font-bold">{`${label}`}</p>
        <p className="intro text-brand-secondary">{`Amount: ${currencySymbol}${payload[0].value.toFixed(2)}`}</p>
      </div>
    );
  }
  return null;
};

const getPrimaryCurrency = (expensesInView: Expense[]): string => {
    if (!expensesInView || expensesInView.length === 0) return 'USD';
    
    const counts: { [key: string]: number } = {};
    for (const expense of expensesInView) {
        counts[expense.currency] = (counts[expense.currency] || 0) + 1;
    }
    
    return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b, 'USD');
};


const Dashboard: React.FC<DashboardProps> = ({ expenses }) => {
  const [view, setView] = useState<TimeView>('Monthly');
  // Initialize date to the most recent expense, or today if no expenses exist.
  const [currentDate, setCurrentDate] = useState(() => expenses.length > 0 ? new Date(expenses[0].date) : new Date());

  // Effect to update the view to the latest expense when expenses are added/deleted.
  useEffect(() => {
    // This ensures that after adding/deleting an expense, the dashboard focuses on the period
    // of the new most recent expense, providing immediate feedback to the user.
    if (expenses.length > 0) {
      setCurrentDate(new Date(expenses[0].date));
    } else {
      // If all expenses are deleted, reset the view to the current date.
      setCurrentDate(new Date());
    }
  }, [expenses.length]); // Dependency on the number of expenses detects additions/deletions.

  const { total, categoryData, trendsData, filteredExpenses } = useMemo(() => processExpensesForCharts(expenses, view, currentDate), [expenses, view, currentDate]);
  
  const primaryCurrency = getPrimaryCurrency(filteredExpenses);
  const currencySymbol = getCurrencySymbol(primaryCurrency);
  const displayDateRange = getDisplayDateRange(view, currentDate);

  const hasDataForView = filteredExpenses.length > 0;

  const handlePrev = () => {
    switch (view) {
      case 'Daily': setCurrentDate(subDays(currentDate, 1)); break;
      case 'Weekly': setCurrentDate(subWeeks(currentDate, 1)); break;
      case 'Monthly': setCurrentDate(subMonths(currentDate, 1)); break;
      case 'Yearly': setCurrentDate(subYears(currentDate, 1)); break;
    }
  };

  const handleNext = () => {
    switch (view) {
      case 'Daily': setCurrentDate(addDays(currentDate, 1)); break;
      case 'Weekly': setCurrentDate(addWeeks(currentDate, 1)); break;
      case 'Monthly': setCurrentDate(addMonths(currentDate, 1)); break;
      case 'Yearly': setCurrentDate(addYears(currentDate, 1)); break;
    }
  };

  const isNextDisabled = useMemo(() => {
    const today = new Date();
    switch (view) {
      case 'Daily': return addDays(currentDate, 1) > today;
      case 'Weekly': return addWeeks(currentDate, 1) > today;
      case 'Monthly': return addMonths(currentDate, 1) > today;
      case 'Yearly': return addYears(currentDate, 1) > today;
      default: return false;
    }
  }, [view, currentDate]);


  return (
    <div className="space-y-6">
      <div className="bg-base-200 p-4 rounded-xl shadow-lg">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <p className="text-gray-400 text-sm">Total Spend ({view})</p>
            <p className="text-4xl font-bold text-white">{currencySymbol}{total.toFixed(2)}</p>
          </div>
          <div className="flex flex-col items-center">
             <div className="flex items-center space-x-2">
                <button onClick={handlePrev} className="p-2 rounded-full bg-base-300/70 hover:bg-brand-primary text-gray-300 hover:text-white transition-colors">
                    <ChevronLeftIcon className="w-5 h-5" />
                </button>
                <p className="text-center font-semibold text-white w-48">{displayDateRange}</p>
                <button onClick={handleNext} disabled={isNextDisabled} className="p-2 rounded-full bg-base-300/70 hover:bg-brand-primary text-gray-300 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    <ChevronRightIcon className="w-5 h-5" />
                </button>
            </div>
          </div>
          <div className="flex items-center space-x-1 bg-base-300 p-1 rounded-lg">
            {(['Daily', 'Weekly', 'Monthly', 'Yearly'] as TimeView[]).map(v => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${view === v ? 'bg-brand-primary text-white' : 'text-gray-300 hover:bg-base-100'}`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {!hasDataForView ? (
         <div className="text-center bg-base-200 p-10 rounded-xl shadow-lg">
            <p className="text-gray-400">No expenses recorded for this period.</p>
         </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-base-200 p-4 rounded-xl shadow-lg">
            <h3 className="text-lg font-bold mb-4 text-white">{view} Spending Trends</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                {view === 'Yearly' ? (
                  <LineChart data={trendsData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                    <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                    <YAxis stroke="#9ca3af" fontSize={12} tickFormatter={(value) => `${currencySymbol}${value}`} />
                    <Tooltip content={<CustomTooltip currencySymbol={currencySymbol} />} cursor={{ fill: 'rgba(79, 70, 229, 0.1)' }}/>
                    <Line type="monotone" dataKey="amount" stroke="#4f46e5" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                ) : (
                  <BarChart data={trendsData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                    <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                    <YAxis stroke="#9ca3af" fontSize={12} tickFormatter={(value) => `${currencySymbol}${value}`} />
                    <Tooltip content={<CustomTooltip currencySymbol={currencySymbol} />} cursor={{ fill: 'rgba(79, 70, 229, 0.1)' }}/>
                    <Bar dataKey="amount" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>
          <div className="bg-base-200 p-4 rounded-xl shadow-lg">
            <h3 className="text-lg font-bold mb-4 text-white">Category Breakdown</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `${currencySymbol}${value.toFixed(2)}`} />
                  <Legend iconSize={10} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;