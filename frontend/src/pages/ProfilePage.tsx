import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/api';
import PostCard from '../components/PostCard';
import CreatePostForm from '../components/CreatePostForm';
import { Loader2, User, Users, FileText, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const ProfilePage = () => {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();

  // Get user data
  const {
    data: userData,
    isLoading: userLoading,
    error: userError,
  } = useQuery({
    queryKey: ['user', userId || 'me'],
    queryFn: () => userId ? apiClient.getUser(parseInt(userId)) : apiClient.getCurrentUser(),
  });

  // Get user posts
  const {
    data: postsData,
    isLoading: postsLoading,
    error: postsError,
  } = useQuery({
    queryKey: ['userPosts', userId || 'me'],
    queryFn: () => apiClient.getFeed({ page: 1, per_page: 20 }), // This should be user-specific posts
    enabled: !!userData,
  });

  const followMutation = useMutation({
    mutationFn: () => userId ? apiClient.followUser(parseInt(userId)) : Promise.resolve(),
    onSuccess: () => {
      queryClient.invalidateQueries(['user', userId || 'me']);
    },
  });

  const unfollowMutation = useMutation({
    mutationFn: () => userId ? apiClient.unfollowUser(parseInt(userId)) : Promise.resolve(),
    onSuccess: () => {
      queryClient.invalidateQueries(['user', userId || 'me']);
    },
  });

  const createPostMutation = useMutation({
    mutationFn: apiClient.createPost,
    onSuccess: () => {
      queryClient.invalidateQueries(['userPosts', userId || 'me']);
    },
  });

  const handleFollow = () => {
    if (userData?.user?.is_following) {
      unfollowMutation.mutate();
    } else {
      followMutation.mutate();
    }
  };

  const handleCreatePost = (content: string, isPublic: boolean) => {
    createPostMutation.mutate({ content, is_public: isPublic });
  };

  if (userLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (userError) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">Failed to load user profile</p>
      </div>
    );
  }

  const user = userData?.user;
  const posts = postsData?.posts || [];
  const isOwnProfile = !userId || currentUser?.id === user?.id;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="card p-6">
        <div className="flex items-start space-x-6">
          {/* Avatar */}
          <div className="h-24 w-24 rounded-full bg-primary-600 flex items-center justify-center">
            <span className="text-2xl font-medium text-white">
              {user?.first_name[0]}{user?.last_name[0]}
            </span>
          </div>

          {/* User Info */}
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {user?.first_name} {user?.last_name}
                </h1>
                <p className="text-gray-500 dark:text-gray-400">@{user?.username}</p>
              </div>

              {!isOwnProfile && (
                <button
                  onClick={handleFollow}
                  disabled={followMutation.isLoading || unfollowMutation.isLoading}
                  className={`btn ${
                    user?.is_following ? 'btn-secondary' : 'btn-primary'
                  }`}
                >
                  {user?.is_following ? 'Unfollow' : 'Follow'}
                </button>
              )}
            </div>

            {user?.bio && (
              <p className="mt-4 text-gray-700 dark:text-gray-300">{user.bio}</p>
            )}

            {/* Stats */}
            <div className="mt-6 flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {user?.followers_count} followers
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {user?.following_count} following
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {user?.posts_count} posts
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Joined {formatDistanceToNow(new Date(user?.created_at || ''), { addSuffix: true })}
                </span>
              </div>
            </div>

            {/* Gramps Integration */}
            {(user?.gramps_person_id || user?.gramps_tree_id) && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Connected to Gramps Family Tree
                </p>
                {user.gramps_person_id && (
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                    Person ID: {user.gramps_person_id}
                  </p>
                )}
                {user.gramps_tree_id && (
                  <p className="text-xs text-blue-600 dark:text-blue-400">
                    Tree ID: {user.gramps_tree_id}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Post Form (only for own profile) */}
      {isOwnProfile && (
        <CreatePostForm onSubmit={handleCreatePost} isLoading={createPostMutation.isLoading} />
      )}

      {/* Posts */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          {isOwnProfile ? 'Your Posts' : `${user?.first_name}'s Posts`}
        </h2>

        {postsLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        ) : postsError ? (
          <div className="text-center py-12">
            <p className="text-red-600 dark:text-red-400">Failed to load posts</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              {isOwnProfile ? 'You haven\'t posted anything yet.' : `${user?.first_name} hasn't posted anything yet.`}
            </p>
          </div>
        ) : (
          posts.map((post: any) => <PostCard key={post.id} post={post} />)
        )}
      </div>
    </div>
  );
};

export default ProfilePage;
