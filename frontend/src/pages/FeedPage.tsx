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
  } = useQuery({
    queryKey: ['feed'],
    queryFn: () => apiClient.getFeed({ page: 1, per_page: 50 }),
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
        {feedData?.posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              No posts yet. Follow some users to see their posts in your feed!
            </p>
          </div>
        ) : (
          feedData?.posts.map((post: any) => <PostCard key={post.id} post={post} />)
        )}
      </div>


    </div>
  );
};

export default FeedPage;
