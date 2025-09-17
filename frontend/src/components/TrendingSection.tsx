import React from 'react';
import { TrendingUp, Hash, Users, Eye } from 'lucide-react';

interface TrendingItem {
  id: string;
  type: 'hashtag' | 'topic';
  content: string;
  posts_count?: number;
  views_count?: number;
  trend: 'up' | 'down' | 'stable';
}

interface TrendingSectionProps {
  trendingItems: TrendingItem[];
  onTrendClick?: (item: TrendingItem) => void;
}

const TrendingSection: React.FC<TrendingSectionProps> = ({
  trendingItems,
  onTrendClick
}) => {
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />;
      default:
        return <TrendingUp className="w-4 h-4 text-gray-500" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600 dark:text-green-400';
      case 'down':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-6">
      <div className="flex items-center space-x-2 mb-4">
        <TrendingUp className="w-5 h-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Trending Now
        </h3>
      </div>
      
      <div className="space-y-3">
        {trendingItems.map((item, index) => (
          <button
            key={item.id}
            onClick={() => onTrendClick?.(item)}
            className="w-full text-left p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-bold text-gray-500 dark:text-gray-400">
                  #{index + 1}
                </span>
                <div className="flex items-center space-x-2">
                  {item.type === 'hashtag' ? (
                    <Hash className="w-4 h-4 text-blue-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-purple-500" />
                  )}
                  <span className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                    {item.content}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {item.posts_count && (
                  <div className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400">
                    <Users className="w-3 h-3" />
                    <span>{item.posts_count}</span>
                  </div>
                )}
                {item.views_count && (
                  <div className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400">
                    <Eye className="w-3 h-3" />
                    <span>{item.views_count}</span>
                  </div>
                )}
                <div className={`flex items-center space-x-1 ${getTrendColor(item.trend)}`}>
                  {getTrendIcon(item.trend)}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
      
      <button className="w-full mt-4 text-center text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium">
        View all trends
      </button>
    </div>
  );
};

export default TrendingSection;


