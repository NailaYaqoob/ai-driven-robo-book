import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { useSession, signIn, signUp, signOut } from '../lib/auth-client';

// Backend base URL, injected at build time (see docusaurus.config.js).
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types
export type Persona = 'student' | 'educator' | 'self_learner' | 'industry_professional' | null;
export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | null;
export type LearningPace = 'accelerated' | 'standard' | 'extended' | null;
export type Language = 'en' | 'ur';

export interface PersonalizationState {
  persona: Persona;
  skillLevel: SkillLevel;
  learningPace: LearningPace;
  language: Language;
  isAuthenticated: boolean;
}

export interface PersonalizationContextValue extends PersonalizationState {
  updatePersona: (persona: Persona) => void;
  updateSkillLevel: (skillLevel: SkillLevel) => void;
  updateLearningPace: (pace: LearningPace) => void;
  updateLanguage: (language: Language) => void;
  setAuthenticated: (isAuth: boolean) => void;
  syncToBackend: () => Promise<void>;
  loadFromBackend: () => Promise<void>;
  resetPreferences: () => void;
  // Better Auth methods
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, preferences?: Partial<PersonalizationState>) => Promise<void>;
  signOut: () => Promise<void>;
}

const defaultState: PersonalizationState = {
  persona: null,
  skillLevel: null,
  learningPace: 'standard',
  language: 'en',
  isAuthenticated: false,
};

export const PersonalizationContext = createContext<PersonalizationContextValue | undefined>(undefined);

const STORAGE_KEY = 'robotics_textbook_user_prefs';

interface Props {
  children: ReactNode;
}

export function PersonalizationProvider({ children }: Props) {
  const [state, setState] = useState<PersonalizationState>(defaultState);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setState(prev => ({ ...prev, ...parsed }));
      }
    } catch (error) {
      console.error('Failed to load preferences from localStorage:', error);
    }
  }, []);

  // Save to localStorage whenever state changes
  useEffect(() => {
    try {
      const toStore = {
        persona: state.persona,
        skillLevel: state.skillLevel,
        learningPace: state.learningPace,
        language: state.language,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
    } catch (error) {
      console.error('Failed to save preferences to localStorage:', error);
    }
  }, [state]);

  const updatePersona = (persona: Persona) => {
    setState(prev => ({ ...prev, persona }));
  };

  const updateSkillLevel = (skillLevel: SkillLevel) => {
    setState(prev => ({ ...prev, skillLevel }));
  };

  const updateLearningPace = (pace: LearningPace) => {
    setState(prev => ({ ...prev, learningPace: pace }));
  };

  const updateLanguage = (language: Language) => {
    setState(prev => ({ ...prev, language }));
  };

  const setAuthenticated = (isAuth: boolean) => {
    setState(prev => ({ ...prev, isAuthenticated: isAuth }));
  };

  const syncToBackend = async () => {
    if (!state.isAuthenticated) {
      console.warn('Cannot sync to backend: user not authenticated');
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.error('No auth token found');
        return;
      }

      const response = await fetch(`${API_URL}/api/personalization/sync-from-localStorage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          persona: state.persona,
          skill_level: state.skillLevel,
          learning_pace: state.learningPace,
          language_preference: state.language,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to sync preferences: ${response.statusText}`);
      }

      console.log('Preferences synced to backend successfully');
    } catch (error) {
      console.error('Failed to sync preferences to backend:', error);
    }
  };

  const loadFromBackend = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.error('No auth token found');
        return;
      }

      const response = await fetch(`${API_URL}/api/personalization/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load preferences: ${response.statusText}`);
      }

      const data = await response.json();
      setState(prev => ({
        ...prev,
        persona: data.persona,
        skillLevel: data.skill_level,
        learningPace: data.learning_pace,
        language: data.language_preference || 'en',
        isAuthenticated: true,
      }));

      console.log('Preferences loaded from backend successfully');
    } catch (error) {
      console.error('Failed to load preferences from backend:', error);
    }
  };

  const resetPreferences = () => {
    setState(defaultState);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Better Auth integration
  const handleSignIn = async (email: string, password: string) => {
    try {
      const response = await signIn({
        email,
        password,
      });

      if (response.error) {
        throw new Error(response.error.message);
      }

      // Load user preferences from backend after successful sign in
      setAuthenticated(true);
      await loadFromBackend();
    } catch (error) {
      console.error('Sign in failed:', error);
      throw error;
    }
  };

  const handleSignUp = async (
    email: string,
    password: string,
    preferences?: Partial<PersonalizationState>
  ) => {
    try {
      const response = await signUp({
        email,
        password,
        name: '',
        ...preferences,
      });

      if (response.error) {
        throw new Error(response.error.message);
      }

      // Update local state with preferences
      if (preferences) {
        setState(prev => ({ ...prev, ...preferences, isAuthenticated: true }));
      } else {
        setAuthenticated(true);
      }

      // Sync preferences to backend
      await syncToBackend();
    } catch (error) {
      console.error('Sign up failed:', error);
      throw error;
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      resetPreferences();
    } catch (error) {
      console.error('Sign out failed:', error);
      throw error;
    }
  };

  const value: PersonalizationContextValue = {
    ...state,
    updatePersona,
    updateSkillLevel,
    updateLearningPace,
    updateLanguage,
    setAuthenticated,
    syncToBackend,
    loadFromBackend,
    resetPreferences,
    signIn: handleSignIn,
    signUp: handleSignUp,
    signOut: handleSignOut,
  };

  return (
    <PersonalizationContext.Provider value={value}>
      {children}
    </PersonalizationContext.Provider>
  );
}
