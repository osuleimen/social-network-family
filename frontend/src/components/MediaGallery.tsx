import React, { useState } from 'react';
import { Media } from '../types';
import { X, Download, Trash2 } from 'lucide-react';

interface MediaGalleryProps {
  media: Media[];
  canDelete?: boolean;
  onDeleteMedia?: (mediaId: number) => void;
}

interface MediaModalProps {
  media: Media;
  isOpen: boolean;
  onClose: () => void;
  canDelete?: boolean;
  onDelete?: (mediaId: number) => void;
}

const MediaModal: React.FC<MediaModalProps> = ({ 
  media, 
  isOpen, 
  onClose, 
  canDelete = false, 
  onDelete 
}) => {
  if (!isOpen) return null;

  const handleDelete = () => {
    if (onDelete && confirm('Are you sure you want to delete this image?')) {
      onDelete(media.id);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
      <div className="relative max-w-4xl max-h-4xl w-full h-full flex items-center justify-center p-4">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
        >
          <X className="h-8 w-8" />
        </button>

        {/* Action Buttons */}
        <div className="absolute top-4 left-4 flex space-x-2 z-10">
          <a
            href={media.gramps_url}
            download={media.original_filename}
            className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
            title="Download"
          >
            <Download className="h-5 w-5" />
          </a>
          
          {canDelete && onDelete && (
            <button
              onClick={handleDelete}
              className="bg-black bg-opacity-50 text-red-400 p-2 rounded-full hover:bg-opacity-70 hover:text-red-300 transition-all"
              title="Delete"
            >
              <Trash2 className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Image */}
        <img
          src={media.gramps_url}
          alt={media.original_filename}
          className="max-w-full max-h-full object-contain"
        />

        {/* Image Info */}
        <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-50 text-white p-3 rounded">
          <h3 className="font-medium truncate">{media.original_filename}</h3>
          <p className="text-sm text-gray-300">
            {(media.file_size / (1024 * 1024)).toFixed(2)} MB • {media.mime_type}
          </p>
        </div>
      </div>
    </div>
  );
};

const MediaGallery: React.FC<MediaGalleryProps> = ({ 
  media, 
  canDelete = false, 
  onDeleteMedia 
}) => {
  const [selectedMedia, setSelectedMedia] = useState<Media | null>(null);

  if (!media || media.length === 0) {
    return null;
  }

  const isImage = (mimeType: string) => mimeType.startsWith('image/');

  const renderMediaGrid = () => {
    const imageMedia = media.filter(m => isImage(m.mime_type));
    
    if (imageMedia.length === 0) return null;

    // Single image
    if (imageMedia.length === 1) {
      return (
        <div className="relative rounded-lg overflow-hidden">
          <img
            src={imageMedia[0].gramps_url}
            alt={imageMedia[0].original_filename}
            className="w-full h-64 object-cover hover:opacity-90 transition-opacity cursor-pointer"
            onClick={() => setSelectedMedia(imageMedia[0])}
          />
          {canDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (onDeleteMedia) onDeleteMedia(imageMedia[0].id);
              }}
              className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
              title="Delete photo"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      );
    }

    // Two images
    if (imageMedia.length === 2) {
      return (
        <div className="grid grid-cols-2 gap-1 rounded-lg overflow-hidden">
          {imageMedia.map((mediaItem) => (
            <div
              key={mediaItem.id}
              className="relative"
            >
              <img
                src={mediaItem.gramps_url}
                alt={mediaItem.original_filename}
                className="w-full h-64 object-cover hover:opacity-90 transition-opacity cursor-pointer"
                onClick={() => setSelectedMedia(mediaItem)}
              />
              {canDelete && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onDeleteMedia) onDeleteMedia(mediaItem.id);
                  }}
                  className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
                  title="Delete photo"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      );
    }

    // Three images
    if (imageMedia.length === 3) {
      return (
        <div className="grid grid-cols-2 gap-1 rounded-lg overflow-hidden">
          <div className="relative row-span-2">
            <img
              src={imageMedia[0].gramps_url}
              alt={imageMedia[0].original_filename}
              className="w-full h-full object-cover hover:opacity-90 transition-opacity cursor-pointer"
              onClick={() => setSelectedMedia(imageMedia[0])}
            />
            {canDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (onDeleteMedia) onDeleteMedia(imageMedia[0].id);
                }}
                className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
                title="Delete photo"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <div className="grid grid-rows-2 gap-1">
            {imageMedia.slice(1, 3).map((mediaItem) => (
              <div
                key={mediaItem.id}
                className="relative"
              >
                <img
                  src={mediaItem.gramps_url}
                  alt={mediaItem.original_filename}
                  className="w-full h-full object-cover hover:opacity-90 transition-opacity cursor-pointer"
                  onClick={() => setSelectedMedia(mediaItem)}
                />
                {canDelete && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onDeleteMedia) onDeleteMedia(mediaItem.id);
                    }}
                    className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
                    title="Delete photo"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Four or more images
    return (
      <div className="grid grid-cols-2 gap-1 rounded-lg overflow-hidden">
        {imageMedia.slice(0, 3).map((mediaItem) => (
          <div
            key={mediaItem.id}
            className="relative"
          >
            <img
              src={mediaItem.gramps_url}
              alt={mediaItem.original_filename}
              className="w-full h-32 object-cover hover:opacity-90 transition-opacity cursor-pointer"
              onClick={() => setSelectedMedia(mediaItem)}
            />
            {canDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (onDeleteMedia) onDeleteMedia(mediaItem.id);
                }}
                className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
                title="Delete photo"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        ))}
        
        {imageMedia.length > 4 ? (
          <div className="relative bg-gray-900 bg-opacity-80 flex items-center justify-center">
            <img
              src={imageMedia[3].gramps_url}
              alt={imageMedia[3].original_filename}
              className="w-full h-32 object-cover absolute inset-0"
            />
            <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center cursor-pointer" onClick={() => setSelectedMedia(imageMedia[3])}>
              <span className="text-white text-xl font-semibold">
                +{imageMedia.length - 3}
              </span>
            </div>
            {canDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (onDeleteMedia) onDeleteMedia(imageMedia[3].id);
                }}
                className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
                title="Delete photo"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        ) : (
          <div className="relative">
            <img
              src={imageMedia[3].gramps_url}
              alt={imageMedia[3].original_filename}
              className="w-full h-32 object-cover hover:opacity-90 transition-opacity cursor-pointer"
              onClick={() => setSelectedMedia(imageMedia[3])}
            />
            {canDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (onDeleteMedia) onDeleteMedia(imageMedia[3].id);
                }}
                className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1.5 rounded-full transition-colors z-10"
                title="Delete photo"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      <div className="mt-3">
        {renderMediaGrid()}
      </div>

      {/* Modal */}
      {selectedMedia && (
        <MediaModal
          media={selectedMedia}
          isOpen={!!selectedMedia}
          onClose={() => setSelectedMedia(null)}
          canDelete={canDelete}
          onDelete={onDeleteMedia}
        />
      )}
    </>
  );
};

export default MediaGallery;
