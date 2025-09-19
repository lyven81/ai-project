
import React, { useState, useRef } from 'react';
import { ExpenseData, expenseCategories, ExpenseItem } from '../types';
import { extractExpenseDataFromImage } from '../services/geminiService';
import { fileToBase64 } from '../utils/fileUtils';
import { Spinner, UploadIcon, XIcon, PlusIcon, TrashIcon, CheckCircleIcon } from './icons/Icons';

interface ReceiptProcessorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (expenseData: ExpenseData) => void;
}

const initialExpenseState: ExpenseData = {
  merchant: '',
  date: new Date().toISOString().split('T')[0],
  total: 0,
  currency: 'USD',
  category: 'Other',
  items: [],
};

const ReceiptProcessorModal: React.FC<ReceiptProcessorModalProps> = ({ isOpen, onClose, onSave }) => {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [expenseData, setExpenseData] = useState<ExpenseData>(initialExpenseState);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetState = () => {
    setImagePreview(null);
    setExpenseData(initialExpenseState);
    setIsLoading(false);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setImagePreview(URL.createObjectURL(file));
    setIsLoading(true);
    setError(null);

    try {
      const base64Image = await fileToBase64(file);
      const extractedData = await extractExpenseDataFromImage(base64Image, file.type);
      setExpenseData(extractedData);
    } catch (err: any) {
      setError(err.message || 'Failed to process receipt. Please enter details manually.');
      setExpenseData(initialExpenseState); // Reset to empty form on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setExpenseData(prev => ({ ...prev, [name]: name === 'total' ? parseFloat(value) || 0 : value }));
  };

  const handleItemChange = (index: number, field: keyof ExpenseItem, value: string | number) => {
    const newItems = [...expenseData.items];
    (newItems[index] as any)[field] = field === 'price' ? parseFloat(value as string) || 0 : value;
    setExpenseData(prev => ({ ...prev, items: newItems }));
  };
  
  const addItem = () => {
    setExpenseData(prev => ({...prev, items: [...prev.items, {name: '', price: 0}]}));
  }

  const removeItem = (index: number) => {
    setExpenseData(prev => ({...prev, items: prev.items.filter((_, i) => i !== index)}));
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(expenseData);
    handleClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-50 p-4">
      <div className="bg-base-200 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div className="flex justify-between items-center p-4 border-b border-base-300">
          <h2 className="text-xl font-bold text-white">Add New Expense</h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-white transition-colors">
            <XIcon className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto">
          {!imagePreview ? (
            <div
              className="border-2 border-dashed border-base-300 rounded-lg p-12 text-center cursor-pointer hover:border-brand-primary transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-400">
                <span className="font-semibold text-brand-primary">Upload a receipt</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="image/*" />
            </div>
          ) : (
            <div className="relative mb-4">
              <img src={imagePreview} alt="Receipt preview" className="rounded-lg w-full max-h-60 object-contain bg-base-100" />
              {isLoading && (
                 <div className="absolute inset-0 bg-black bg-opacity-60 flex flex-col justify-center items-center rounded-lg">
                    <Spinner className="w-10 h-10" />
                    <p className="text-white mt-2 font-semibold">Analyzing receipt...</p>
                 </div>
              )}
            </div>
          )}

          {error && <div className="bg-red-900/50 border border-red-700 text-red-300 p-3 rounded-lg text-sm my-4">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="merchant" className="block text-sm font-medium text-gray-300">Merchant</label>
                <input type="text" name="merchant" value={expenseData.merchant} onChange={handleChange} className="mt-1 w-full bg-base-300 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-brand-primary focus:border-brand-primary" required />
              </div>
              <div>
                <label htmlFor="date" className="block text-sm font-medium text-gray-300">Date</label>
                <input type="date" name="date" value={expenseData.date} onChange={handleChange} className="mt-1 w-full bg-base-300 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-brand-primary focus:border-brand-primary" required />
              </div>
            </div>
             <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
               <div>
                <label htmlFor="total" className="block text-sm font-medium text-gray-300">Total</label>
                <input type="number" name="total" step="0.01" value={expenseData.total} onChange={handleChange} className="mt-1 w-full bg-base-300 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-brand-primary focus:border-brand-primary" required />
              </div>
              <div>
                <label htmlFor="currency" className="block text-sm font-medium text-gray-300">Currency</label>
                <input type="text" name="currency" value={expenseData.currency} onChange={handleChange} className="mt-1 w-full bg-base-300 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-brand-primary focus:border-brand-primary" required />
              </div>
              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-300">Category</label>
                <select name="category" value={expenseData.category} onChange={handleChange} className="mt-1 w-full bg-base-300 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-brand-primary focus:border-brand-primary">
                  {expenseCategories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                </select>
              </div>
            </div>
            
            <div>
                <h3 className="text-md font-medium text-gray-300 mb-2">Items</h3>
                <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                    {expenseData.items.map((item, index) => (
                        <div key={index} className="flex items-center gap-2">
                            <input type="text" placeholder="Item Name" value={item.name} onChange={(e) => handleItemChange(index, 'name', e.target.value)} className="w-full bg-base-300 border border-gray-600 rounded-md p-2 text-white focus:ring-brand-primary focus:border-brand-primary"/>
                            <input type="number" placeholder="Price" value={item.price} onChange={(e) => handleItemChange(index, 'price', e.target.value)} className="w-28 bg-base-300 border border-gray-600 rounded-md p-2 text-white focus:ring-brand-primary focus:border-brand-primary"/>
                            <button type="button" onClick={() => removeItem(index)} className="p-2 text-gray-400 hover:text-red-500">
                                <TrashIcon className="w-5 h-5"/>
                            </button>
                        </div>
                    ))}
                </div>
                 <button type="button" onClick={addItem} className="mt-2 flex items-center gap-2 text-sm text-brand-primary hover:text-indigo-400">
                    <PlusIcon className="w-4 h-4"/> Add Item
                 </button>
            </div>
          </form>
        </div>
        
        <div className="p-4 bg-base-200 border-t border-base-300 flex justify-end space-x-3">
          <button onClick={handleClose} className="px-4 py-2 text-sm font-medium text-gray-300 bg-base-300 rounded-lg hover:bg-gray-600 transition-colors">Cancel</button>
          <button onClick={handleSubmit} className="px-4 py-2 text-sm font-medium text-white bg-brand-secondary rounded-lg hover:bg-emerald-500 transition-colors flex items-center gap-2">
            <CheckCircleIcon className="w-5 h-5"/>
            Save Expense
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReceiptProcessorModal;
