import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

interface User {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  bio?: string;
  followers_count?: number;
  following_count?: number;
  friends_count?: number;
}

interface FriendRequest {
  id: number;
  status: string;
  created_at: string;
  requester?: User;
  recipient?: User;
}

interface FriendsAndFollowsProps {
  userId: number;
  currentUserId: number;
}

export const FriendsAndFollows: React.FC<FriendsAndFollowsProps> = ({
  userId,
  currentUserId
}) => {
  const [activeTab, setActiveTab] = useState<'followers' | 'following' | 'friends' | 'requests'>('followers');
  const [followers, setFollowers] = useState<User[]>([]);
  const [following, setFollowing] = useState<User[]>([]);
  const [friends, setFriends] = useState<User[]>([]);
  const [friendRequests, setFriendRequests] = useState<FriendRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [followStatus, setFollowStatus] = useState<{[key: number]: boolean}>({});

  useEffect(() => {
    if (activeTab === 'followers') {
      fetchFollowers();
    } else if (activeTab === 'following') {
      fetchFollowing();
    } else if (activeTab === 'friends') {
      fetchFriends();
    } else if (activeTab === 'requests') {
      fetchFriendRequests();
    }
  }, [activeTab, userId]);

  const fetchFollowers = async () => {
    setLoading(true);
    try {
      const response = await apiService.get(`/followers/${userId}`);
      setFollowers(response.data.followers?.map((item: any) => item.user) || []);
    } catch (error) {
      console.error('Error fetching followers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFollowing = async () => {
    setLoading(true);
    try {
      const response = await apiService.get(`/following/${userId}`);
      setFollowing(response.data.following?.map((item: any) => item.user) || []);
    } catch (error) {
      console.error('Error fetching following:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFriends = async () => {
    setLoading(true);
    try {
      const response = await apiService.get(`/friends/${userId}`);
      setFriends(response.data.friends?.map((item: any) => item.user) || []);
    } catch (error) {
      console.error('Error fetching friends:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFriendRequests = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/pending-requests');
      setFriendRequests(response.data.pending_requests || []);
    } catch (error) {
      console.error('Error fetching friend requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (targetUserId: number) => {
    try {
      const isFollowing = followStatus[targetUserId];
      if (isFollowing) {
        await apiService.post(`/unfollow/${targetUserId}`);
        setFollowStatus(prev => ({ ...prev, [targetUserId]: false }));
      } else {
        await apiService.post(`/follow/${targetUserId}`);
        setFollowStatus(prev => ({ ...prev, [targetUserId]: true }));
      }
    } catch (error) {
      console.error('Error toggling follow:', error);
    }
  };

  const handleFriendRequest = async (targetUserId: number) => {
    try {
      await apiService.post(`/send-request/${targetUserId}`);
      alert('Запрос в друзья отправлен');
    } catch (error) {
      console.error('Error sending friend request:', error);
    }
  };

  const handleAcceptRequest = async (requestId: number) => {
    try {
      await apiService.post(`/accept-request/${requestId}`);
      setFriendRequests(prev => prev.filter(req => req.id !== requestId));
      alert('Запрос в друзья принят');
    } catch (error) {
      console.error('Error accepting friend request:', error);
    }
  };

  const handleDeclineRequest = async (requestId: number) => {
    try {
      await apiService.post(`/decline-request/${requestId}`);
      setFriendRequests(prev => prev.filter(req => req.id !== requestId));
    } catch (error) {
      console.error('Error declining friend request:', error);
    }
  };

  const renderUserCard = (user: User, showActions: boolean = true) => (
    <div key={user.id} className="flex items-center justify-between p-4 border-b border-gray-200">
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.username || 'User'}
              className="h-12 w-12 rounded-full object-cover"
            />
          ) : (
            <div className="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
              <span className="text-gray-600">👤</span>
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {user.first_name && user.last_name 
              ? `${user.first_name} ${user.last_name}`
              : user.username || 'Пользователь'
            }
          </p>
          {user.bio && (
            <p className="text-sm text-gray-500 truncate">{user.bio}</p>
          )}
          <div className="flex space-x-4 text-xs text-gray-400 mt-1">
            {user.followers_count !== undefined && (
              <span>{user.followers_count} подписчиков</span>
            )}
            {user.following_count !== undefined && (
              <span>{user.following_count} подписок</span>
            )}
            {user.friends_count !== undefined && (
              <span>{user.friends_count} друзей</span>
            )}
          </div>
        </div>
      </div>
      
      {showActions && user.id !== currentUserId && (
        <div className="flex space-x-2">
          <button
            onClick={() => handleFollow(user.id)}
            className={`px-3 py-1 text-xs rounded-full ${
              followStatus[user.id]
                ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {followStatus[user.id] ? 'Отписаться' : 'Подписаться'}
          </button>
          <button
            onClick={() => handleFriendRequest(user.id)}
            className="px-3 py-1 text-xs rounded-full bg-green-600 text-white hover:bg-green-700"
          >
            В друзья
          </button>
        </div>
      )}
    </div>
  );

  const renderFriendRequest = (request: FriendRequest) => (
    <div key={request.id} className="flex items-center justify-between p-4 border-b border-gray-200">
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          {request.requester?.avatar_url ? (
            <img
              src={request.requester.avatar_url}
              alt={request.requester.username || 'User'}
              className="h-12 w-12 rounded-full object-cover"
            />
          ) : (
            <div className="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
              <span className="text-gray-600">👤</span>
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {request.requester?.first_name && request.requester?.last_name 
              ? `${request.requester.first_name} ${request.requester.last_name}`
              : request.requester?.username || 'Пользователь'
            }
          </p>
          <p className="text-sm text-gray-500">Хочет добавить вас в друзья</p>
          <p className="text-xs text-gray-400">
            {new Date(request.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={() => handleAcceptRequest(request.id)}
          className="px-3 py-1 text-xs rounded-full bg-green-600 text-white hover:bg-green-700"
        >
          Принять
        </button>
        <button
          onClick={() => handleDeclineRequest(request.id)}
          className="px-3 py-1 text-xs rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300"
        >
          Отклонить
        </button>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { key: 'followers', label: 'Подписчики', count: followers.length },
            { key: 'following', label: 'Подписки', count: following.length },
            { key: 'friends', label: 'Друзья', count: friends.length },
            ...(userId === currentUserId ? [{ key: 'requests', label: 'Запросы', count: friendRequests.length }] : [])
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="max-h-96 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {activeTab === 'followers' && (
              <>
                {followers.length === 0 ? (
                  <div className="text-center p-8 text-gray-500">
                    <div className="text-4xl mb-2">👥</div>
                    <p>Нет подписчиков</p>
                  </div>
                ) : (
                  followers.map(user => renderUserCard(user))
                )}
              </>
            )}

            {activeTab === 'following' && (
              <>
                {following.length === 0 ? (
                  <div className="text-center p-8 text-gray-500">
                    <div className="text-4xl mb-2">👤</div>
                    <p>Нет подписок</p>
                  </div>
                ) : (
                  following.map(user => renderUserCard(user))
                )}
              </>
            )}

            {activeTab === 'friends' && (
              <>
                {friends.length === 0 ? (
                  <div className="text-center p-8 text-gray-500">
                    <div className="text-4xl mb-2">🤝</div>
                    <p>Нет друзей</p>
                  </div>
                ) : (
                  friends.map(user => renderUserCard(user, false))
                )}
              </>
            )}

            {activeTab === 'requests' && (
              <>
                {friendRequests.length === 0 ? (
                  <div className="text-center p-8 text-gray-500">
                    <div className="text-4xl mb-2">📨</div>
                    <p>Нет запросов в друзья</p>
                  </div>
                ) : (
                  friendRequests.map(request => renderFriendRequest(request))
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};
