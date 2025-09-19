import { Expense, TimeView, ExpenseCategory, expenseCategories } from '../types';
import { startOfDay, startOfWeek, startOfMonth, startOfYear, endOfDay, endOfWeek, endOfMonth, endOfYear, format } from 'date-fns';

interface ChartDataPoint {
  name: string;
  amount: number;
}

interface CategoryDataPoint {
  name: ExpenseCategory;
  value: number;
  // Fix: Added index signature to satisfy recharts data prop type for Pie component.
  [key: string]: any;
}

export const getDisplayDateRange = (view: TimeView, date: Date): string => {
    switch (view) {
        case 'Daily':
            return format(date, 'MMMM d, yyyy');
        case 'Weekly':
            const weekStart = startOfWeek(date, { weekStartsOn: 1 });
            const weekEnd = endOfWeek(date, { weekStartsOn: 1 });
            if (format(weekStart, 'MMM') === format(weekEnd, 'MMM')) {
                 return `${format(weekStart, 'MMM d')} - ${format(weekEnd, 'd, yyyy')}`;
            }
            return `${format(weekStart, 'MMM d')} - ${format(weekEnd, 'MMM d, yyyy')}`;
        case 'Monthly':
            return format(date, 'MMMM yyyy');
        case 'Yearly':
            return format(date, 'yyyy');
    }
}

export const processExpensesForCharts = (expenses: Expense[], view: TimeView, date: Date) => {
  const now = date;
  let startDate: Date, endDate: Date;

  switch (view) {
    case 'Daily':
      startDate = startOfDay(now);
      endDate = endOfDay(now);
      break;
    case 'Weekly':
      startDate = startOfWeek(now, { weekStartsOn: 1 });
      endDate = endOfWeek(now, { weekStartsOn: 1 });
      break;
    case 'Monthly':
      startDate = startOfMonth(now);
      endDate = endOfMonth(now);
      break;
    case 'Yearly':
      startDate = startOfYear(now);
      endDate = endOfYear(now);
      break;
  }
  
  const filteredExpenses = expenses.filter(e => {
    const expenseDate = new Date(e.date);
    return expenseDate >= startDate && expenseDate <= endDate;
  });

  const total = filteredExpenses.reduce((sum, e) => sum + e.total, 0);

  const categoryData: CategoryDataPoint[] = expenseCategories.map(category => ({
      name: category,
      value: filteredExpenses
        .filter(e => e.category === category)
        .reduce((sum, e) => sum + e.total, 0),
  })).filter(c => c.value > 0);

  let trendsData: ChartDataPoint[] = [];

  if (view === 'Daily') { // Not very useful, but for consistency
    trendsData = [{ name: format(now, 'MMM d'), amount: total }];
  } else if (view === 'Weekly') {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    trendsData = days.map((day, i) => {
        const dayStart = startOfWeek(now, { weekStartsOn: 1 });
        dayStart.setDate(dayStart.getDate() + i);
        const dayOfWeek = (dayStart.getDay() + 6) % 7; // Monday is 0, Sunday is 6
        return {
            name: day,
            amount: filteredExpenses.filter(e => (new Date(e.date).getDay() + 6) % 7 === dayOfWeek).reduce((sum, e) => sum + e.total, 0),
        };
    });
  } else if (view === 'Monthly') {
    const weeksInMonth = Math.ceil(new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate() / 7);
    trendsData = Array.from({ length: weeksInMonth }, (_, i) => {
        const weekStart = new Date(startOfMonth(now));
        weekStart.setDate(weekStart.getDate() + i * 7);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekEnd.getDate() + 6);

        return {
            name: `Week ${i + 1}`,
            amount: filteredExpenses
                .filter(e => {
                    const d = new Date(e.date);
                    return d >= weekStart && d <= weekEnd;
                })
                .reduce((sum, e) => sum + e.total, 0),
        };
    });
  } else if (view === 'Yearly') {
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      trendsData = months.map((month, i) => ({
          name: month,
          amount: filteredExpenses
              .filter(e => new Date(e.date).getMonth() === i)
              .reduce((sum, e) => sum + e.total, 0),
      }));
  }

  return { total, categoryData, trendsData, filteredExpenses };
};

export const getCurrencySymbol = (currencyCode: string) => {
    const symbols: { [key: string]: string } = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
    };
    return symbols[currencyCode.toUpperCase()] || currencyCode;
};