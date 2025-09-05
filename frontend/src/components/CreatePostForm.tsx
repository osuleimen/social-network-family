import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Send, Eye, EyeOff, Image, X } from 'lucide-react';
import MediaUpload from './MediaUpload';

const postSchema = z.object({
  content: z.string().min(1, 'Post content is required').max(1000, 'Post is too long'),
});

type PostFormData = z.infer<typeof postSchema>;

interface CreatePostFormProps {
  onSubmit: (content: string, isPublic: boolean, postId?: number) => void;
  isLoading?: boolean;
}

const CreatePostForm = ({ onSubmit, isLoading }: CreatePostFormProps) => {
  const [isPublic, setIsPublic] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [showMediaUpload, setShowMediaUpload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [createdPostId, setCreatedPostId] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
  });

  const content = watch('content', '');

  const handleFormSubmit = (data: PostFormData) => {
    onSubmit(data.content, isPublic);
    reset();
    setSelectedFiles([]);
    setShowMediaUpload(false);
    setCreatedPostId(null);
  };

  const handleFilesSelected = (files: File[]) => {
    setSelectedFiles(files);
  };

  return (
    <div className="card p-6">
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <div>
          <textarea
            {...register('content')}
            rows={3}
            className="input resize-none"
            placeholder="What's on your mind?"
            disabled={isLoading}
          />
          {errors.content && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.content.message}</p>
          )}
        </div>

        {/* Media Upload Section */}
        {showMediaUpload && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">Add Photos</h4>
              <button
                type="button"
                onClick={() => setShowMediaUpload(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <MediaUpload
              onFilesSelected={handleFilesSelected}
            />
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Privacy toggle */}
            <button
              type="button"
              onClick={() => setIsPublic(!isPublic)}
              className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              {isPublic ? (
                <>
                  <Eye className="h-4 w-4" />
                  <span>Public</span>
                </>
              ) : (
                <>
                  <EyeOff className="h-4 w-4" />
                  <span>Private</span>
                </>
              )}
            </button>

            {/* Media toggle */}
            <button
              type="button"
              onClick={() => setShowMediaUpload(!showMediaUpload)}
              className={`flex items-center space-x-2 text-sm transition-colors ${
                showMediaUpload || selectedFiles.length > 0
                  ? 'text-primary-600 dark:text-primary-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
              }`}
            >
              <Image className="h-4 w-4" />
              <span>
                {selectedFiles.length > 0 
                  ? `${selectedFiles.length} photo${selectedFiles.length > 1 ? 's' : ''}`
                  : 'Add Photos'
                }
              </span>
            </button>

            {/* Preview toggle */}
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              {showPreview ? 'Hide Preview' : 'Show Preview'}
            </button>
          </div>

          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="btn btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
            <span>Post</span>
          </button>
        </div>

        {/* Preview */}
        {showPreview && content && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Preview:</h4>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <p className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">{content}</p>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default CreatePostForm;
