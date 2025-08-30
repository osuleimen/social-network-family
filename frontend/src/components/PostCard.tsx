import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { Post } from '../types';
import apiClient from '../services/api';
import { Heart, MessageCircle, MoreHorizontal, Edit, Trash2, Eye, EyeOff } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface PostCardProps {
  post: Post;
}

const PostCard = ({ post }: PostCardProps) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showComments, setShowComments] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content);

  const likeMutation = useMutation({
    mutationFn: () => apiClient.likePost(post.id),
    onSuccess: () => {
      queryClient.invalidateQueries(['feed']);
      queryClient.invalidateQueries(['post', post.id]);
    },
  });

  const unlikeMutation = useMutation({
    mutationFn: () => apiClient.unlikePost(post.id),
    onSuccess: () => {
      queryClient.invalidateQueries(['feed']);
      queryClient.invalidateQueries(['post', post.id]);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.deletePost(post.id),
    onSuccess: () => {
      queryClient.invalidateQueries(['feed']);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (content: string) => apiClient.updatePost(post.id, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries(['feed']);
      queryClient.invalidateQueries(['post', post.id]);
      setIsEditing(false);
    },
  });

  const handleLike = () => {
    if (post.likes_count > 0) {
      unlikeMutation.mutate();
    } else {
      likeMutation.mutate();
    }
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this post?')) {
      deleteMutation.mutate();
    }
  };

  const handleUpdate = () => {
    if (editContent.trim() && editContent !== post.content) {
      updateMutation.mutate(editContent);
    } else {
      setIsEditing(false);
      setEditContent(post.content);
    }
  };

  const isOwnPost = user?.id === post.author.id;
  const isLiked = post.likes_count > 0; // This should be determined by checking if current user liked the post

  return (
    <div className="card p-6">
      {/* Post Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center">
            <span className="text-sm font-medium text-white">
              {post.author.first_name[0]}{post.author.last_name[0]}
            </span>
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-white">
              {post.author.first_name} {post.author.last_name}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              @{post.author.username} • {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
            </p>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <MoreHorizontal className="h-5 w-5 text-gray-400" />
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 z-10">
              {isOwnPost && (
                <>
                  <button
                    onClick={() => {
                      setIsEditing(true);
                      setShowMenu(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      handleDelete();
                      setShowMenu(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </button>
                </>
              )}
              <div className="flex items-center px-4 py-2 text-sm text-gray-500 dark:text-gray-400">
                {post.is_public ? (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    Public
                  </>
                ) : (
                  <>
                    <EyeOff className="h-4 w-4 mr-2" />
                    Private
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Post Content */}
      <div className="mb-4">
        {isEditing ? (
          <div className="space-y-2">
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="input resize-none"
              rows={3}
            />
            <div className="flex space-x-2">
              <button
                onClick={handleUpdate}
                disabled={updateMutation.isLoading}
                className="btn btn-primary text-sm"
              >
                Save
              </button>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setEditContent(post.content);
                }}
                className="btn btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{post.content}</p>
        )}
      </div>

      {/* Post Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-6">
          <button
            onClick={handleLike}
            disabled={likeMutation.isLoading || unlikeMutation.isLoading}
            className={`flex items-center space-x-2 text-sm transition-colors ${
              isLiked
                ? 'text-red-600 dark:text-red-400'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <Heart className={`h-5 w-5 ${isLiked ? 'fill-current' : ''}`} />
            <span>{post.likes_count}</span>
          </button>

          <button
            onClick={() => setShowComments(!showComments)}
            className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <MessageCircle className="h-5 w-5" />
            <span>{post.comments_count}</span>
          </button>
        </div>
      </div>

      {/* Comments Section */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            Comments feature coming soon...
          </p>
        </div>
      )}
    </div>
  );
};

export default PostCard;
