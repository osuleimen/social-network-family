import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import PostCard from '../components/PostCard';
import { Search, Loader2 } from 'lucide-react';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const {
    data: searchData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: () => apiClient.searchPosts(searchQuery, { page: 1, per_page: 20 }),
    enabled: !!searchQuery,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchQuery(query.trim());
    }
  };

  const posts = searchData?.posts || [];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Search Posts</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find posts by keywords
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search posts..."
            className="input pl-10"
          />
        </div>
        <button type="submit" className="btn btn-primary w-full">
          Search
        </button>
      </form>

      {/* Search Results */}
      {searchQuery && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Search results for "{searchQuery}"
          </h2>

          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600 dark:text-red-400">Failed to search posts</p>
            </div>
          ) : posts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                No posts found for "{searchQuery}"
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {posts.map((post: any) => <PostCard key={post.id} post={post} />)}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchPage;
