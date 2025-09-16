import React, { useState } from 'react';
import { SearchBar } from '../components/SearchBar';
import { FriendsAndFollows } from '../components/FriendsAndFollows';
import { AIContentGenerator } from '../components/AIContentGenerator';
import { useAuth } from '../contexts/AuthContext';

export const FeaturesDemo: React.FC = () => {
  const { user } = useAuth();
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [selectedHashtag, setSelectedHashtag] = useState<string | null>(null);

  const handleUserSelect = (userId: number) => {
    setSelectedUserId(userId);
    setSelectedHashtag(null);
  };

  const handleHashtagSelect = (hashtag: string) => {
    setSelectedHashtag(hashtag);
    setSelectedUserId(null);
  };

  const handleAIContentGenerated = (content: string, hashtags: string[]) => {
    console.log('AI Generated Content:', content);
    console.log('AI Generated Hashtags:', hashtags);
    alert(`AI сгенерировал контент:\n\n${content}\n\nХэштеги: ${hashtags.join(', ')}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          🚀 Новые возможности социальной сети
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Демонстрация расширенного функционала Instagram-аналога
        </p>
      </div>

      {/* Search Demo */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">🔍 Умный поиск</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Поиск пользователей, хэштегов с автодополнением и предложениями
        </p>
        <SearchBar
          onUserSelect={handleUserSelect}
          onHashtagSelect={handleHashtagSelect}
          placeholder="Попробуйте найти пользователя или хэштег..."
        />
        {selectedUserId && (
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900 rounded-md">
            <p className="text-blue-800 dark:text-blue-200">
              Выбран пользователь с ID: {selectedUserId}
            </p>
          </div>
        )}
        {selectedHashtag && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-900 rounded-md">
            <p className="text-green-800 dark:text-green-200">
              Выбран хэштег: #{selectedHashtag}
            </p>
          </div>
        )}
      </div>

      {/* AI Content Generator Demo */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">🤖 AI Генератор контента</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Автоматическая генерация описаний и хэштегов с помощью Gemini AI
        </p>
        <AIContentGenerator
          onContentGenerated={handleAIContentGenerated}
          language="ru"
        />
      </div>

      {/* Friends and Follows Demo */}
      {user && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">👥 Система друзей и подписок</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Управление подписками, друзьями и запросами в друзья
          </p>
          <FriendsAndFollows
            userId={user.id}
            currentUserId={user.id}
          />
        </div>
      )}

      {/* Features List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">✨ Реализованные возможности</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">👤 Пользователи</h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• Роли: Администратор, Модератор, Пользователь</li>
              <li>• Система банов и блокировок</li>
              <li>• Многоязычная поддержка (RU, EN, KK)</li>
              <li>• Интеграция с Gramps</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">📝 Посты</h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• Хэштеги и упоминания</li>
              <li>• Геолокация</li>
              <li>• Уровни приватности</li>
              <li>• AI-генерация контента</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">🤝 Социальные функции</h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• Система подписок/фолловинга</li>
              <li>• Система друзей</li>
              <li>• Уведомления в реальном времени</li>
              <li>• Лайки и комментарии</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">🔧 Администрирование</h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• Панель администратора</li>
              <li>• Модерация контента</li>
              <li>• Управление пользователями</li>
              <li>• Статистика и аналитика</li>
            </ul>
          </div>
        </div>
      </div>

      {/* API Endpoints */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">🔗 API Endpoints</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h3 className="font-semibold mb-2">Социальные функции</h3>
            <ul className="space-y-1 text-gray-600 dark:text-gray-400">
              <li><code>/api/follow/{"{id}"}</code> - Подписка</li>
              <li><code>/api/friends/{"{id}"}</code> - Друзья</li>
              <li><code>/api/notifications/</code> - Уведомления</li>
              <li><code>/api/feed/home</code> - Лента новостей</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">AI и поиск</h3>
            <ul className="space-y-1 text-gray-600 dark:text-gray-400">
              <li><code>/api/ai/generate-description</code> - AI описание</li>
              <li><code>/api/search/users</code> - Поиск пользователей</li>
              <li><code>/api/search/hashtags</code> - Поиск хэштегов</li>
              <li><code>/api/admin/users</code> - Админ панель</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
