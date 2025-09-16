import React from 'react';
import { Plus, User } from 'lucide-react';

interface Story {
  id: number;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    avatar_url?: string;
  };
  media_url: string;
  created_at: string;
  viewed?: boolean;
}

interface StoriesSectionProps {
  stories: Story[];
  onAddStory?: () => void;
  onViewStory?: (storyId: number) => void;
}

const StoriesSection: React.FC<StoriesSectionProps> = ({
  stories,
  onAddStory,
  onViewStory
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-6">
      <div className="flex space-x-4 overflow-x-auto pb-2">
        {/* Add Story Button */}
        <div className="flex-shrink-0">
          <button
            onClick={onAddStory}
            className="flex flex-col items-center space-y-2 group"
          >
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center group-hover:bg-gray-300 dark:group-hover:bg-gray-600 transition-colors">
                <Plus className="w-6 h-6 text-gray-600 dark:text-gray-400" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                <Plus className="w-3 h-3 text-white" />
              </div>
            </div>
            <span className="text-xs text-gray-600 dark:text-gray-400 font-medium">
              Your Story
            </span>
          </button>
        </div>

        {/* Stories */}
        {stories.map((story) => (
          <div key={story.id} className="flex-shrink-0">
            <button
              onClick={() => onViewStory?.(story.id)}
              className="flex flex-col items-center space-y-2 group"
            >
              <div className="relative">
                <div className={`w-16 h-16 rounded-full p-0.5 ${
                  story.viewed 
                    ? 'bg-gray-300 dark:bg-gray-600' 
                    : 'bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500'
                }`}>
                  <div className="w-full h-full rounded-full bg-white dark:bg-gray-800 p-0.5">
                    {story.user.avatar_url ? (
                      <img
                        src={story.user.avatar_url}
                        alt={`${story.user.first_name} ${story.user.last_name}`}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                        <User className="w-6 h-6 text-gray-500" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <span className="text-xs text-gray-600 dark:text-gray-400 font-medium max-w-16 truncate">
                {story.user.first_name}
              </span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StoriesSection;

