import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import PostCard from '../components/PostCard';
import { Loader2 } from 'lucide-react';

const ExplorePage = () => {
  const [page, setPage] = useState(1);

  const {
    data: exploreData,
    isLoading,
    error,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useQuery({
    queryKey: ['explore', page],
    queryFn: () => apiClient.getExploreFeed({ page, per_page: 10 }),
    keepPreviousData: true,
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">Failed to load explore feed</p>
      </div>
    );
  }

  const posts = exploreData?.posts || [];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Explore</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover posts from all users
        </p>
      </div>

      {/* Posts */}
      <div className="space-y-6">
        {posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              No posts to explore yet.
            </p>
          </div>
        ) : (
          posts.map((post) => <PostCard key={post.id} post={post} />)
        )}
      </div>

      {/* Load More */}
      {hasNextPage && (
        <div className="text-center">
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="btn btn-outline"
          >
            {isFetchingNextPage ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              'Load More'
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ExplorePage;
