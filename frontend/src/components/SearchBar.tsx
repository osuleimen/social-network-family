import React, { useState, useEffect, useRef } from 'react';
import apiService from '../services/api';

interface SearchSuggestion {
  type: 'user' | 'hashtag';
  id: string | number;
  title: string;
  subtitle?: string;
  avatar?: string;
}

interface SearchBarProps {
  onUserSelect?: (userId: number) => void;
  onHashtagSelect?: (hashtag: string) => void;
  placeholder?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onUserSelect,
  onHashtagSelect,
  placeholder = "Поиск пользователей, хэштегов..."
}) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (query.length >= 2) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
      setIsOpen(false);
    }
  }, [query]);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const response = await apiService.get(`/search/suggestions?q=${encodeURIComponent(query)}`);
      setSuggestions(response.data.suggestions || []);
      setIsOpen(true);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    if (suggestion.type === 'user' && onUserSelect) {
      onUserSelect(Number(suggestion.id));
    } else if (suggestion.type === 'hashtag' && onHashtagSelect) {
      onHashtagSelect(suggestion.id as string);
    }
    setQuery('');
    setIsOpen(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className="relative" ref={searchRef}>
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        {loading && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>

      {/* Suggestions Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((suggestion, index) => (
            <div
              key={`${suggestion.type}-${suggestion.id}-${index}`}
              onClick={() => handleSuggestionClick(suggestion)}
              className="flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
            >
              <div className="flex-shrink-0 mr-3">
                {suggestion.type === 'user' ? (
                  suggestion.avatar ? (
                    <img
                      src={suggestion.avatar}
                      alt={suggestion.title}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                      <span className="text-gray-600 text-sm">👤</span>
                    </div>
                  )
                ) : (
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-blue-600 text-sm">#</span>
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {suggestion.title}
                </p>
                {suggestion.subtitle && (
                  <p className="text-xs text-gray-500 truncate">
                    {suggestion.subtitle}
                  </p>
                )}
              </div>
              <div className="flex-shrink-0">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  suggestion.type === 'user' 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {suggestion.type === 'user' ? 'Пользователь' : 'Хэштег'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results */}
      {isOpen && query.length >= 2 && suggestions.length === 0 && !loading && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4">
          <div className="text-center text-gray-500">
            <div className="text-2xl mb-2">🔍</div>
            <p>Ничего не найдено</p>
            <p className="text-sm">Попробуйте другой запрос</p>
          </div>
        </div>
      )}
    </div>
  );
};
