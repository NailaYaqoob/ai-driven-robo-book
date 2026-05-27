// Simple auth client that works with our FastAPI backend.
// REACT_APP_API_URL is injected at build time (see docusaurus.config.js).
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const TOKEN_KEY = 'auth_token';

// The backend returns a JWT as `access_token`; persist it so authenticated
// requests (personalization sync/load) can send `Authorization: Bearer <token>`.
function storeToken(data: any) {
  if (typeof localStorage !== 'undefined' && data?.access_token) {
    localStorage.setItem(TOKEN_KEY, data.access_token);
  }
}

function clearToken() {
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export const authClient = {
  async signIn({ email, password }: { email: string; password: string }) {
    const response = await fetch(`${API_URL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Sign in failed' }));
      return { error: { message: error.message || 'Sign in failed' } };
    }

    const data = await response.json();
    storeToken(data);
    return data;
  },

  async signUp({ email, password, name, ...preferences }: any) {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: name, ...preferences }),
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Sign up failed' }));
      return { error: { message: error.message || 'Sign up failed' } };
    }

    const data = await response.json();
    storeToken(data);
    return data;
  },

  async signOut() {
    const response = await fetch(`${API_URL}/api/auth/signout`, {
      method: 'POST',
      credentials: 'include',
    });

    // Always drop the local token, even if the network call fails.
    clearToken();

    if (!response.ok) {
      throw new Error('Sign out failed');
    }

    return await response.json();
  },

  async getSession() {
    const response = await fetch(`${API_URL}/api/auth/session`, {
      credentials: 'include',
    });

    if (!response.ok) {
      return { user: null };
    }

    return await response.json();
  },
};

export const signIn = authClient.signIn;
export const signUp = authClient.signUp;
export const signOut = authClient.signOut;
export const useSession = () => {
  // This is a simplified hook - in production you'd use React Query or SWR
  return { data: null, isLoading: false };
};
