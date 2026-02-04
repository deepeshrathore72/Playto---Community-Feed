import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Users API
export const usersApi = {
  list: () => api.get('/users/'),
  get: (id) => api.get(`/users/${id}/`),
  create: (data) => api.post('/users/', data),
  getCurrentUser: () => api.get('/users/me/'),
  login: (username) => api.post('/users/me/', { username }),
  logout: () => api.delete('/users/me/'),
};

// Posts API
export const postsApi = {
  list: (page = 1) => api.get(`/posts/?page=${page}`),
  get: (id) => api.get(`/posts/${id}/`),
  create: (content) => api.post('/posts/', { content }),
};

// Comments API
export const commentsApi = {
  getByPost: (postId) => api.get(`/comments/post/${postId}/`),
  create: (data) => api.post('/comments/', data),
  delete: (id) => api.delete(`/comments/${id}/`),
};

// Likes API
export const likesApi = {
  togglePostLike: (postId) => api.post(`/likes/post/${postId}/toggle/`),
  toggleCommentLike: (commentId) => api.post(`/likes/comment/${commentId}/toggle/`),
};

// Leaderboard API
export const leaderboardApi = {
  get: (limit = 5, hours = 24) => api.get(`/leaderboard/?limit=${limit}&hours=${hours}`),
  getUserKarma: (userId) => api.get(`/leaderboard/user/${userId}/`),
};

export default api;
