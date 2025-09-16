import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthResponse, ApiError } from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'https://my.ozimiz.org/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/unified-auth/refresh`, {}, {
                headers: {
                  Authorization: `Bearer ${refreshToken}`,
                },
              });

              const { access_token } = response.data;
              localStorage.setItem('access_token', access_token);
              
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh token failed, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/auth';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // User endpoints
  async getCurrentUser() {
    const response = await this.client.get('/users/profile');
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/auth/logout');
    return response.data;
  }

  async getUsers(params?: { page?: number; per_page?: number; search?: string }) {
    const response = await this.client.get('/users', { params });
    return response.data;
  }

  async getUser(userId: number) {
    const response = await this.client.get(`/users/${userId}`);
    return response.data;
  }

  async updateProfile(userData: Partial<{
    first_name: string;
    last_name: string;
    bio: string;
    avatar_url: string;
    gramps_person_id: string;
    gramps_tree_id: string;
  }>) {
    const response = await this.client.put('/users/profile', userData);
    return response.data;
  }

  async followUser(userId: number) {
    const response = await this.client.post(`/follow/${userId}`);
    return response.data;
  }

  async unfollowUser(userId: number) {
    const response = await this.client.post(`/unfollow/${userId}`);
    return response.data;
  }

  async getFollowers(userId: number, params?: { page?: number; per_page?: number }) {
    const response = await this.client.get(`/followers/${userId}`, { params });
    return response.data;
  }

  async getFollowing(userId: number, params?: { page?: number; per_page?: number }) {
    const response = await this.client.get(`/following/${userId}`, { params });
    return response.data;
  }

  // Post endpoints
  async createPost(postData: { content: string; is_public?: boolean }) {
    const response = await this.client.post('/posts', {
      caption: postData.content,
      privacy: postData.is_public ? 'public' : 'private'
    });
    return response.data;
  }

  async getPost(postId: number) {
    const response = await this.client.get(`/posts/${postId}`);
    return response.data;
  }

  async updatePost(postId: number, postData: Partial<{ content: string; is_public: boolean }>) {
    const response = await this.client.put(`/posts/${postId}`, postData);
    return response.data;
  }

  async deletePost(postId: number) {
    const response = await this.client.delete(`/posts/${postId}`);
    return response.data;
  }

  async likePost(postId: number) {
    const response = await this.client.post(`/posts/${postId}/like`);
    return response.data;
  }

  async unlikePost(postId: number) {
    const response = await this.client.post(`/posts/${postId}/unlike`);
    return response.data;
  }

  // Comment endpoints
  async createComment(postId: number, commentData: { content: string }) {
    const response = await this.client.post(`/post/${postId}/comments`, commentData);
    return response.data;
  }

  async getComments(postId: number) {
    const response = await this.client.get(`/post/${postId}/comments`);
    return response.data;
  }

  async updateComment(commentId: number, commentData: { content: string }) {
    const response = await this.client.put(`/comments/${commentId}`, commentData);
    return response.data;
  }

  async deleteComment(commentId: number) {
    const response = await this.client.delete(`/comments/${commentId}`);
    return response.data;
  }

  // Media endpoints
  async uploadMediaToPost(postId: number, files: FileList) {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });
    
    const response = await this.client.post(`/posts/${postId}/media`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getPostMedia(postId: number) {
    const response = await this.client.get(`/posts/${postId}/media`);
    return response.data;
  }

  async deleteMedia(mediaId: number) {
    const response = await this.client.delete(`/media/${mediaId}`);
    return response.data;
  }

  async getMediaUrl(mediaId: number) {
    const response = await this.client.get(`/media/${mediaId}/url`);
    return response.data;
  }

  // Feed endpoints
  async getFeed(params?: { page?: number; per_page?: number }) {
    const response = await this.client.get('/feed', { params });
    return response.data;
  }

  async getExploreFeed(params?: { page?: number; per_page?: number }) {
    const response = await this.client.get('/feed/explore', { params });
    return response.data;
  }

  async getUserPosts(userId: number, params?: { page?: number; per_page?: number }) {
    const response = await this.client.get(`/feed/user/${userId}`, { params });
    return response.data;
  }

  async searchPosts(query: string, params?: { page?: number; per_page?: number }) {
    const response = await this.client.get('/feed/search', { 
      params: { q: query, ...params } 
    });
    return response.data;
  }

  // Utility method to set auth token
  setAuthToken(token: string) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // Utility method to remove auth token
  removeAuthToken() {
    delete this.client.defaults.headers.common['Authorization'];
  }

  // Generic HTTP methods for compatibility
  async get(url: string, config?: any) {
    return this.client.get(url, config);
  }

  async post(url: string, data?: any, config?: any) {
    return this.client.post(url, data, config);
  }

  async put(url: string, data?: any, config?: any) {
    return this.client.put(url, data, config);
  }

  async delete(url: string, config?: any) {
    return this.client.delete(url, config);
  }

  // Unified Authentication methods
  async requestCode(identifier: string) {
    const response = await this.client.post('/unified-auth/request-code', { identifier });
    return response.data;
  }

  async verifyCode(identifier: string, code: string) {
    const response = await this.client.post('/unified-auth/verify-code', { 
      identifier, 
      code 
    });
    return response.data;
  }

  async resendCode(identifier: string) {
    const response = await this.client.post('/unified-auth/resend-code', { identifier });
    return response.data;
  }

  async forceSendCode(identifier: string) {
    const response = await this.client.post('/unified-auth/force-send-code', { identifier });
    return response.data;
  }

  async refreshToken() {
    const response = await this.client.post('/unified-auth/refresh');
    return response.data;
  }

  // Legacy SMS Authentication methods (for compatibility)
  async requestSMSCode(phone_number: string) {
    return this.requestCode(phone_number);
  }

  async verifySMSCode(phone_number: string, verification_code: string) {
    return this.verifyCode(phone_number, verification_code);
  }

  async resendSMSCode(phone_number: string) {
    return this.resendCode(phone_number);
  }

  // Legacy Email Authentication methods (for compatibility)
  async requestEmailCode(email: string) {
    return this.requestCode(email);
  }

  async verifyEmailCode(email: string, verification_code: string) {
    return this.verifyCode(email, verification_code);
  }

  async resendEmailCode(email: string) {
    return this.resendCode(email);
  }

  // Google OAuth methods
  async googleLogin() {
    const response = await this.client.get('/auth/google/login');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
