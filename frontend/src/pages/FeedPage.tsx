import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/api';
import PostCard from '../components/PostCard';
import CreatePostForm from '../components/CreatePostForm';
import StoriesSection from '../components/StoriesSection';
import QuickActions from '../components/QuickActions';
import TrendingSection from '../components/TrendingSection';
import { Loader2 } from 'lucide-react';

const FeedPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  // Mock data for Instagram-like features
  const mockStories = [
    {
      id: 1,
      user: { id: 1, first_name: 'Айдар', last_name: 'Нурланов', avatar_url: undefined },
      media_url: '',
      created_at: new Date().toISOString(),
      viewed: false
    },
    {
      id: 2,
      user: { id: 2, first_name: 'Асель', last_name: 'Тулеуова', avatar_url: undefined },
      media_url: '',
      created_at: new Date().toISOString(),
      viewed: true
    }
  ];

  const mockTrending = [
    { id: '1', type: 'hashtag' as const, content: 'Алматы', posts_count: 1250, trend: 'up' as const },
    { id: '2', type: 'hashtag' as const, content: 'Казахстан', posts_count: 890, trend: 'up' as const },
    { id: '3', type: 'hashtag' as const, content: 'Весна2025', posts_count: 650, trend: 'stable' as const },
    { id: '4', type: 'topic' as const, content: 'Новые технологии', views_count: 15000, trend: 'up' as const },
    { id: '5', type: 'hashtag' as const, content: 'Спорт', posts_count: 420, trend: 'down' as const }
  ];

  const {
    data: feedData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['feed'],
    queryFn: () => apiClient.getExploreFeed({ page: 1, per_page: 50 }),
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
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Stories Section */}
      <StoriesSection 
        stories={mockStories}
        onAddStory={() => console.log('Add story')}
        onViewStory={(id) => console.log('View story', id)}
      />

      {/* Quick Actions */}
      <QuickActions
        onCreatePost={() => console.log('Create post')}
        onAddStory={() => console.log('Add story')}
        onCreateReel={() => console.log('Create reel')}
        onCheckIn={() => console.log('Check in')}
        onFindFriends={() => console.log('Find friends')}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Feed */}
        <div className="lg:col-span-2 space-y-6">
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

        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Trending Section */}
          <TrendingSection
            trendingItems={mockTrending}
            onTrendClick={(item) => console.log('Trend clicked', item)}
          />
        </div>
      </div>
    </div>
  );
};

export default FeedPage;
