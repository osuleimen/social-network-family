import React, { useState, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';
import { Image, X, Upload, AlertCircle } from 'lucide-react';

interface MediaUploadProps {
  postId?: number;
  onUploadComplete?: (uploadedMedia: any[]) => void;
  onFilesSelected?: (files: File[]) => void;
  disabled?: boolean;
}

interface FilePreview {
  file: File;
  preview: string;
  id: string;
}

const MediaUpload: React.FC<MediaUploadProps> = ({
  postId,
  onUploadComplete,
  onFilesSelected,
  disabled = false
}) => {
  const [selectedFiles, setSelectedFiles] = useState<FilePreview[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: (files: FileList) => {
      if (!postId) throw new Error('Post ID is required for upload');
      return apiClient.uploadMediaToPost(postId, files);
    },
    onSuccess: (data) => {
      setSelectedFiles([]);
      setUploadError(null);
      if (postId) {
        queryClient.invalidateQueries({ queryKey: ['feed'] });
        queryClient.invalidateQueries({ queryKey: ['post', postId] });
      }
      onUploadComplete?.(data.uploaded_media || []);
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || 'Failed to upload files';
      setUploadError(errorMessage);
    }
  });

  const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const MAX_FILES = 10;

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      return `File "${file.name}" is not a supported image format. Please use JPEG, PNG, GIF, or WebP.`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File "${file.name}" is too large. Maximum size is 10MB.`;
    }
    return null;
  };

  const handleFiles = (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    const errors: string[] = [];
    const validFiles: File[] = [];

    // Check total file count
    if (selectedFiles.length + fileArray.length > MAX_FILES) {
      setUploadError(`You can only upload up to ${MAX_FILES} files at once.`);
      return;
    }

    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        validFiles.push(file);
      }
    });

    if (errors.length > 0) {
      setUploadError(errors.join(' '));
      return;
    }

    setUploadError(null);

    // Create previews for valid files
    const newPreviews: FilePreview[] = validFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      id: `${file.name}-${Date.now()}-${Math.random()}`
    }));

    setSelectedFiles(prev => [...prev, ...newPreviews]);
    onFilesSelected?.(validFiles);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const removeFile = (id: string) => {
    setSelectedFiles(prev => {
      const updated = prev.filter(file => file.id !== id);
      // Revoke object URL to prevent memory leaks
      const fileToRemove = prev.find(file => file.id === id);
      if (fileToRemove) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return updated;
    });
  };

  const handleUpload = () => {
    if (selectedFiles.length === 0) return;

    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(filePreview => {
      dataTransfer.items.add(filePreview.file);
    });

    uploadMutation.mutate(dataTransfer.files);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  // Clean up preview URLs on unmount
  React.useEffect(() => {
    return () => {
      selectedFiles.forEach(file => {
        URL.revokeObjectURL(file.preview);
      });
    };
  }, []);

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={disabled ? undefined : handleDrop}
        onClick={disabled ? undefined : openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ALLOWED_FILE_TYPES.join(',')}
          onChange={handleFileInput}
          className="hidden"
          disabled={disabled}
        />

        <div className="space-y-2">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <Image className="h-full w-full" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              Drop images here or click to browse
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              JPEG, PNG, GIF, WebP up to 10MB each (max {MAX_FILES} files)
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {uploadError && (
        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400 text-sm">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* File Previews */}
      {selectedFiles.length > 0 && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {selectedFiles.map((filePreview) => (
              <div key={filePreview.id} className="relative group">
                <div className="relative aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                  <img
                    src={filePreview.preview}
                    alt={filePreview.file.name}
                    className="w-full h-full object-cover"
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(filePreview.id);
                    }}
                    className="absolute top-1 right-1 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 truncate">
                  {filePreview.file.name}
                </p>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          {postId && (
            <div className="flex justify-end">
              <button
                onClick={handleUpload}
                disabled={uploadMutation.isPending || selectedFiles.length === 0}
                className="btn btn-primary flex items-center space-x-2"
              >
                {uploadMutation.isPending ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                <span>
                  {uploadMutation.isPending ? 'Uploading...' : `Upload ${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''}`}
                </span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MediaUpload;
