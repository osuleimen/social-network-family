import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/api';
import PostCard from '../components/PostCard';
import CreatePostForm from '../components/CreatePostForm';
import { Loader2 } from 'lucide-react';

const FeedPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const {
    data: feedData,
    isLoading,
    error,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useQuery({
    queryKey: ['feed', page],
    queryFn: () => apiClient.getFeed({ page, per_page: 10 }),
    keepPreviousData: true,
  });

  const createPostMutation = useMutation({
    mutationFn: apiClient.createPost,
    onSuccess: () => {
      queryClient.invalidateQueries(['feed']);
    },
  });

  const handleCreatePost = (content: string, isPublic: boolean) => {
    createPostMutation.mutate({ content, is_public: isPublic });
  };

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
        <p className="text-red-600 dark:text-red-400">Failed to load feed</p>
      </div>
    );
  }

  const posts = feedData?.posts || [];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Create Post Form */}
      <CreatePostForm onSubmit={handleCreatePost} isLoading={createPostMutation.isLoading} />

      {/* Posts */}
      <div className="space-y-6">
        {posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              No posts yet. Follow some users to see their posts in your feed!
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

export default FeedPage;
