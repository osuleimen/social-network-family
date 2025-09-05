import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { Comment } from '../types';
import apiClient from '../services/api';
import { MessageCircle, Send, Edit, Trash2, MoreHorizontal } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface CommentsSectionProps {
  postId: number;
}

interface CommentItemProps {
  comment: Comment;
  onEdit: (commentId: number, content: string) => void;
  onDelete: (commentId: number) => void;
}

const CommentItem: React.FC<CommentItemProps> = ({ comment, onEdit, onDelete }) => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [showMenu, setShowMenu] = useState(false);

  const isOwnComment = user?.id === comment.author_id;

  const handleEdit = () => {
    if (editContent.trim() && editContent !== comment.content) {
      onEdit(comment.id, editContent);
      setIsEditing(false);
    } else {
      setIsEditing(false);
      setEditContent(comment.content);
    }
  };

  return (
    <div className="flex space-x-3 py-3">
      <div className="flex-shrink-0">
        <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
          <span className="text-xs font-medium text-white">
            {comment.author.first_name[0]}{comment.author.last_name[0]}
          </span>
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {comment.author.first_name} {comment.author.last_name}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
              </span>
            </div>
            
            {isOwnComment && (
              <div className="relative">
                <button
                  onClick={() => setShowMenu(!showMenu)}
                  className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
                >
                  <MoreHorizontal className="h-4 w-4 text-gray-400" />
                </button>
                
                {showMenu && (
                  <div className="absolute right-0 mt-1 w-32 bg-white dark:bg-gray-700 rounded-md shadow-lg border border-gray-200 dark:border-gray-600 z-10">
                    <button
                      onClick={() => {
                        setIsEditing(true);
                        setShowMenu(false);
                      }}
                      className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                    >
                      <Edit className="h-3 w-3 mr-2" />
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        onDelete(comment.id);
                        setShowMenu(false);
                      }}
                      className="flex items-center w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-600"
                    >
                      <Trash2 className="h-3 w-3 mr-2" />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {isEditing ? (
            <div className="space-y-2">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full text-sm bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={2}
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleEdit}
                  className="text-xs bg-primary-600 hover:bg-primary-700 text-white px-2 py-1 rounded"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditContent(comment.content);
                  }}
                  className="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
              {comment.content}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

const CommentsSection: React.FC<CommentsSectionProps> = ({ postId }) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [newComment, setNewComment] = useState('');

  const { data: commentsData, isLoading } = useQuery({
    queryKey: ['comments', postId],
    queryFn: () => apiClient.getComments(postId),
  });

  const createCommentMutation = useMutation({
    mutationFn: (content: string) => apiClient.createComment(postId, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', postId] });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      setNewComment('');
    },
  });

  const updateCommentMutation = useMutation({
    mutationFn: ({ commentId, content }: { commentId: number; content: string }) =>
      apiClient.updateComment(commentId, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', postId] });
    },
  });

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId: number) => apiClient.deleteComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', postId] });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });

  const handleSubmitComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      createCommentMutation.mutate(newComment.trim());
    }
  };

  const handleEditComment = (commentId: number, content: string) => {
    updateCommentMutation.mutate({ commentId, content });
  };

  const handleDeleteComment = (commentId: number) => {
    if (confirm('Are you sure you want to delete this comment?')) {
      deleteCommentMutation.mutate(commentId);
    }
  };

  const comments = commentsData?.comments || [];

  return (
    <div className="space-y-4">
      {/* Add Comment Form */}
      <form onSubmit={handleSubmitComment} className="flex space-x-3">
        <div className="flex-shrink-0">
          <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
            <span className="text-xs font-medium text-white">
              {user?.first_name[0]}{user?.last_name[0]}
            </span>
          </div>
        </div>
        <div className="flex-1">
          <div className="relative">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows={2}
            />
            <button
              type="submit"
              disabled={!newComment.trim() || createCommentMutation.isPending}
              className="absolute bottom-2 right-2 p-1 text-primary-600 hover:text-primary-700 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </form>

      {/* Comments List */}
      <div className="space-y-1">
        {isLoading ? (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
          </div>
        ) : comments.length > 0 ? (
          comments.map((comment: Comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              onEdit={handleEditComment}
              onDelete={handleDeleteComment}
            />
          ))
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No comments yet. Be the first to comment!
          </p>
        )}
      </div>
    </div>
  );
};

export default CommentsSection;
