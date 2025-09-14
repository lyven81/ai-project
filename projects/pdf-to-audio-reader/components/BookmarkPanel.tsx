
import React, { useState } from 'react';
import { Bookmark } from '../types';
import { BookmarkIcon } from './icons/BookmarkIcon';
import { TrashIcon } from './icons/TrashIcon';

interface BookmarkPanelProps {
  bookmarks: Bookmark[];
  onAddBookmark: (note: string) => void;
  onRemoveBookmark: (id: number) => void;
  onGoToBookmark: (bookmark: Bookmark) => void;
}

export const BookmarkPanel: React.FC<BookmarkPanelProps> = ({ bookmarks, onAddBookmark, onRemoveBookmark, onGoToBookmark }) => {
  const [note, setNote] = useState('');

  const handleAddClick = () => {
    if (note.trim()) {
      onAddBookmark(note);
      setNote('');
    }
  };

  return (
    <div className="bg-primary p-4 rounded-lg">
      <h3 className="text-lg font-semibold text-teal-accent mb-3 flex items-center">
        <BookmarkIcon className="w-5 h-5 mr-2" />
        Bookmarks
      </h3>
      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Add a note..."
          className="flex-grow bg-accent border-highlight rounded p-2 text-text-main text-sm focus:outline-none focus:ring-2 focus:ring-teal-accent"
        />
        <button
          onClick={handleAddClick}
          className="bg-teal-accent text-primary px-3 py-1 rounded-md font-semibold text-sm hover:bg-opacity-80 transition-opacity"
        >
          Add
        </button>
      </div>
      <div className="max-h-32 overflow-y-auto space-y-2 pr-2">
        {bookmarks.length === 0 ? (
            <p className="text-text-dim text-sm text-center py-4">No bookmarks yet.</p>
        ) : (
            bookmarks.map(bookmark => (
                <div key={bookmark.id} className="bg-accent p-2 rounded-md flex justify-between items-start gap-2">
                    <div className="flex-grow cursor-pointer" onClick={() => onGoToBookmark(bookmark)}>
                        <p className="text-text-main text-sm font-semibold">{bookmark.note}</p>
                        <p className="text-text-dim text-xs italic">"{bookmark.previewText}"</p>
                    </div>
                    <button onClick={() => onRemoveBookmark(bookmark.id)} className="text-highlight hover:text-red-500 p-1">
                        <TrashIcon className="w-4 h-4" />
                    </button>
                </div>
            ))
        )}
      </div>
    </div>
  );
};
