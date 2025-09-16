import React from 'react';
import { Camera, Video, FileText, MapPin, Users, Heart } from 'lucide-react';

interface QuickAction {
  id: string;
  icon: React.ReactNode;
  label: string;
  color: string;
  onClick: () => void;
}

interface QuickActionsProps {
  onCreatePost?: () => void;
  onAddStory?: () => void;
  onCreateReel?: () => void;
  onCheckIn?: () => void;
  onFindFriends?: () => void;
}

const QuickActions: React.FC<QuickActionsProps> = ({
  onCreatePost,
  onAddStory,
  onCreateReel,
  onCheckIn,
  onFindFriends
}) => {
  const actions: QuickAction[] = [
    {
      id: 'post',
      icon: <FileText className="w-5 h-5" />,
      label: 'Post',
      color: 'bg-blue-500 hover:bg-blue-600',
      onClick: onCreatePost || (() => {})
    },
    {
      id: 'story',
      icon: <Camera className="w-5 h-5" />,
      label: 'Story',
      color: 'bg-purple-500 hover:bg-purple-600',
      onClick: onAddStory || (() => {})
    },
    {
      id: 'reel',
      icon: <Video className="w-5 h-5" />,
      label: 'Reel',
      color: 'bg-pink-500 hover:bg-pink-600',
      onClick: onCreateReel || (() => {})
    },
    {
      id: 'checkin',
      icon: <MapPin className="w-5 h-5" />,
      label: 'Check-in',
      color: 'bg-green-500 hover:bg-green-600',
      onClick: onCheckIn || (() => {})
    },
    {
      id: 'friends',
      icon: <Users className="w-5 h-5" />,
      label: 'Find Friends',
      color: 'bg-orange-500 hover:bg-orange-600',
      onClick: onFindFriends || (() => {})
    }
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Quick Actions
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={action.onClick}
            className={`${action.color} text-white rounded-lg p-4 flex flex-col items-center space-y-2 transition-all duration-200 transform hover:scale-105 active:scale-95`}
          >
            {action.icon}
            <span className="text-sm font-medium">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;

