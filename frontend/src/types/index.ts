export interface User {
  id: string;
  username?: string;
  email?: string;
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  avatar_media_id?: string;
  is_active?: boolean;
  is_verified?: boolean;
  verified?: boolean;
  created_at: string;
  gramps_person_id?: string;
  gramps_tree_id?: string;
  followers_count?: number;
  following_count?: number;
  posts_count?: number;
  is_following?: boolean;
  auth_method?: string;
  phone_number?: string;
  role?: string;
  is_banned?: boolean;
  banned_until?: string;
  ban_reason?: string;
  birth_date?: string;
  date_of_birth?: string;
  updated_at?: string;
  private_account?: boolean;
  profile_slug?: string;
  pronouns?: string;
  status?: string;
  website?: string;
  location?: string;
}

export interface Media {
  id: string;
  filename?: string;
  storage_key?: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  gramps_media_id?: string;
  gramps_url?: string;
  url?: string;
  post_id?: string;
  uploaded_by?: number;
  uploader?: User;
  created_at: string;
}

export interface Post {
  id: string;
  caption: string;
  content?: string; // For backward compatibility
  privacy: string;
  created_at: string;
  updated_at: string;
  author: User;
  author_id: string;
  likes_count: number;
  comments_count: number;
  user_liked?: boolean;
  media: Media[];
  visibility?: string;
  hashtags?: string[];
  mentions?: string[];
  location_name?: string;
  latitude?: number;
  longitude?: number;
  ai_generated_description?: string;
  ai_generated_hashtags?: string[];
  is_edited?: boolean;
  edit_count?: number;
  is_deleted?: boolean;
}

export interface Comment {
  id: number;
  content: string;
  post_id: number;
  author_id: number;
  created_at: string;
  updated_at: string;
  author: User;
}

export interface Like {
  id: number;
  user_id: number;
  post_id: number;
  created_at: string;
}

export interface Follow {
  id: number;
  follower_id: number;
  followed_id: number;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  type: string;
  title: string;
  message: string;
  data?: any;
  is_read: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  pages: number;
  current_page: number;
}

export interface AuthResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface ApiError {
  error: string;
  details?: any;
}
