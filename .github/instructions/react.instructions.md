---
description: React Frontend Development Instructions
applyTo: 'src/frontend/**'
---

# React Frontend Development Instructions

**Framework:** React 18 + TypeScript + Redux + Vite + Material-UI  
**Target Performance:** API <500ms, Cache >80% hit rate, FCP <2s

## Architecture Overview

### Technology Stack
- **React 18** with Concurrent Features for enhanced UX
- **TypeScript** for type safety and better developer experience
- **Redux Toolkit** for predictable state management
- **Vite** for fast development and optimized builds
- **Material-UI (MUI)** for consistent, accessible UI components
- **React Router** for client-side navigation
- **Axios** for HTTP requests with interceptors
- **Telegram Mini App SDK** for seamless integration
- **React Query** (Optional) for server state management and caching

### System Design Principles
1. **Component-Driven**: Reusable, composable components
2. **Type-Safe**: Full TypeScript coverage
3. **Performance-First**: Code splitting, lazy loading, memoization
4. **State Management**: Redux for global state, hooks for local state
5. **Accessibility**: WCAG 2.1 AA compliance
6. **Responsive Design**: Mobile-first approach (Telegram Mini App)

## Clean Architecture Principles

The React frontend follows clean architecture to maximize testability, maintainability, and flexibility:

### Core Layers

```
┌─────────────────────────────────────────┐
│  PRESENTATION LAYER                     │
│  Pages, Components, UI Rendering        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  STATE MANAGEMENT LAYER                 │
│  Redux Store, Slices, Selectors         │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  BUSINESS LOGIC LAYER                   │
│  Hooks, Custom Logic, Validators        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  DATA ACCESS LAYER                      │
│  Services, API Calls, Local Storage     │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. **Presentation Layer** (Components & Pages)
- **Responsibility**: Render UI and capture user input
- **Dependencies**: Material-UI components, styles, hooks
- **Must NOT contain**: API calls, Redux dispatches, business logic

```typescript
// ✅ GOOD - Presentation layer (pure UI)
const MealCard: FC<MealCardProps> = ({ meal, onSelect }) => {
  return (
    <Card onClick={() => onSelect(meal.id)} sx={{ cursor: 'pointer' }}>
      <CardContent>
        <Typography variant="h6">{meal.foodDescription}</Typography>
        <Typography color="textSecondary">{meal.calories} cal</Typography>
      </CardContent>
    </Card>
  );
};

// ❌ BAD - Mixing presentation with business logic
const MealCard: FC<MealCardProps> = ({ mealId }) => {
  const meal = await mealApi.getMeal(mealId); // API call in component!
  const result = await complexBusinessLogic(meal); // Logic in component!
  return <div>{result}</div>;
};
```

#### 2. **State Management Layer** (Redux)
- **Responsibility**: Centralized state, actions, selectors
- **Dependencies**: Redux Toolkit, thunks for async operations
- **Must NOT contain**: UI rendering, direct API calls beyond thunks

```typescript
// slices/mealsSlice.ts - Redux layer
export const fetchMeals = createAsyncThunk(
  'meals/fetchMeals',
  async ({ userId, page }: FetchMealsParams, { rejectWithValue }) => {
    try {
      const response = await mealApi.getMeals(userId, page);
      return response.data.meals;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error));
    }
  }
);

const mealsSlice = createSlice({
  name: 'meals',
  initialState,
  reducers: {
    selectMeal: (state, action) => {
      state.selectedMealId = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchMeals.fulfilled, (state, action) => {
      state.meals = action.payload;
      state.loading = false;
    });
  },
});

// Selectors - query state (memoized)
export const selectMeals = (state: RootState) => state.meals.meals;
export const selectMealsLoading = (state: RootState) => state.meals.loading;
export const selectMealsError = (state: RootState) => state.meals.error;
```

#### 3. **Business Logic Layer** (Custom Hooks)
- **Responsibility**: Orchestrate state, derived logic, side effects
- **Dependencies**: Redux, other hooks
- **Must NOT contain**: UI components, direct API calls

```typescript
// hooks/useMealManagement.ts - Business logic layer
export function useMealManagement() {
  const dispatch = useAppDispatch();
  const meals = useAppSelector(selectMeals);
  const loading = useAppSelector(selectMealsLoading);
  const selectedMealId = useAppSelector(selectSelectedMealId);
  
  // Derived state - calculate based on current state
  const selectedMeal = useMemo(
    () => meals.find(m => m.id === selectedMealId),
    [meals, selectedMealId]
  );
  
  // Business logic - operations that manipulate state
  const handleSelectMeal = useCallback((mealId: string) => {
    if (!meals.some(m => m.id === mealId)) {
      throw new Error('Meal not found');
    }
    dispatch(selectMeal(mealId));
  }, [dispatch, meals]);
  
  // Async operations
  const loadUserMeals = useCallback(
    (userId: string, page: number) => {
      dispatch(fetchMeals({ userId, page }));
    },
    [dispatch]
  );
  
  return {
    meals,
    selectedMeal,
    loading,
    handleSelectMeal,
    loadUserMeals,
  };
}

// Usage in component
const MealsContainer: FC = () => {
  const { meals, loading, handleSelectMeal } = useMealManagement();
  
  return (
    <div>
      {meals.map(meal => (
        <MealCard
          key={meal.id}
          meal={meal}
          onSelect={handleSelectMeal}
        />
      ))}
    </div>
  );
};
```

#### 4. **Data Access Layer** (Services)
- **Responsibility**: External communication (API, local storage, Telegram)
- **Dependencies**: Axios, Telegram SDK, browser APIs
- **Must NOT contain**: Redux dispatch, React components

```typescript
// services/api/mealApi.ts - Data access layer
import axiosInstance from './axiosConfig';
import { Meal, CreateMealRequest } from '@/types';

export const mealApi = {
  // Pure functions - no side effects
  getMeals: async (userId: string, page: number = 1) => {
    return axiosInstance.get(`/meals`, {
      params: { userId, page },
    });
  },
  
  createMeal: async (payload: CreateMealRequest) => {
    return axiosInstance.post('/meals', payload);
  },
  
  deleteMeal: async (mealId: string) => {
    return axiosInstance.delete(`/meals/${mealId}`);
  },
};

// services/storage/localStorageService.ts - Data access layer
export const storageService = {
  saveAuthToken: (token: string) => {
    localStorage.setItem('authToken', token);
  },
  
  getAuthToken: (): string | null => {
    return localStorage.getItem('authToken');
  },
  
  clearAuthToken: () => {
    localStorage.removeItem('authToken');
  },
};
```

### Clean Architecture File Structure

```
src/frontend/src/
│
├── pages/                          # PRESENTATION LAYER
│   ├── HomePage.tsx                # Page components that use hooks + Redux
│   ├── MealsPage.tsx
│   ├── SettingsPage.tsx
│   └── __tests__/
│
├── components/                     # PRESENTATION LAYER
│   ├── Common/
│   │   ├── Header.tsx              # Pure UI components (no logic)
│   │   ├── Footer.tsx
│   │   └── Loading.tsx
│   ├── Meals/
│   │   ├── MealCard.tsx            # Presentation - receives data via props
│   │   ├── MealList.tsx            # Connects to business logic hooks
│   │   └── MealAnalysis.tsx
│   └── __tests__/                  # Component tests
│
├── store/                          # STATE MANAGEMENT LAYER
│   ├── store.ts                    # Redux store configuration
│   ├── slices/
│   │   ├── mealsSlice.ts           # Async thunks + reducers
│   │   ├── authSlice.ts
│   │   └── uiSlice.ts
│   └── selectors.ts                # Memoized state queries
│
├── hooks/                          # BUSINESS LOGIC LAYER
│   ├── useMealManagement.ts        # Orchestrate Redux + derived logic
│   ├── useAuth.ts                  # Authentication logic
│   ├── useMeals.ts                 # Meal-specific logic
│   ├── useApi.ts                   # Generic API call logic
│   └── __tests__/
│
├── services/                       # DATA ACCESS LAYER
│   ├── api/
│   │   ├── mealApi.ts              # Pure API functions
│   │   ├── authApi.ts
│   │   └── axiosConfig.ts          # Axios instance with interceptors
│   ├── telegram/
│   │   └── telegramService.ts      # Telegram Mini App integration
│   └── storage/
│       └── localStorageService.ts  # Browser storage access
│
├── types/                          # SHARED TYPES (cross-layer)
│   ├── index.ts
│   ├── models.ts                   # Domain models
│   ├── api.ts                      # API request/response types
│   └── redux.ts                    # Redux state types
│
├── utils/                          # SHARED UTILITIES (cross-layer)
│   ├── formatters.ts               # Pure functions (no side effects)
│   ├── validators.ts               # Validation logic
│   ├── errorHandler.ts             # Error transformation
│   └── constants.ts                # Constants
│
├── styles/                         # PRESENTATION LAYER
│   ├── index.css
│   ├── variables.css
│   └── animations.css
│
└── themes/                         # PRESENTATION LAYER
    ├── lightTheme.ts
    ├── darkTheme.ts
    └── index.ts
```

### Dependency Flow (Always Inward)

```
Components/Pages
        ↓
   Custom Hooks (useMealManagement, useAuth, etc.)
        ↓
Redux Slices (mealsSlice, authSlice, etc.)
        ↓
Services (mealApi, telegramService, storageService)
        ↓
External APIs / Browser APIs / Telegram SDK

✅ ALLOWED: Components can use hooks
✅ ALLOWED: Hooks can use Redux and services
✅ ALLOWED: Redux can use services for async thunks
✅ ALLOWED: Services can call external APIs

❌ BLOCKED: Services cannot use components
❌ BLOCKED: Services cannot dispatch to Redux
❌ BLOCKED: Redux cannot depend on components
❌ BLOCKED: Components cannot directly call services
```

### Testing Strategy Aligned with Clean Architecture

```typescript
// Test 1: Pure presentation component (no logic)
describe('MealCard', () => {
  it('renders meal information correctly', () => {
    const mockMeal: Meal = { id: '1', foodDescription: 'Pizza', calories: 450 };
    const { getByText } = render(
      <MealCard meal={mockMeal} onSelect={vi.fn()} />
    );
    expect(getByText('Pizza')).toBeInTheDocument();
  });
});

// Test 2: Business logic hook (no components, mock services)
describe('useMealManagement', () => {
  it('loads meals when requested', async () => {
    const { result } = renderHook(() => useMealManagement(), {
      wrapper: ({ children }) => <Provider store={store}>{children}</Provider>,
    });
    
    act(() => {
      result.current.loadUserMeals('user-123', 1);
    });
    
    await waitFor(() => {
      expect(result.current.meals).toHaveLength(3);
    });
  });
});

// Test 3: Redux slice (pure functions, no React dependencies)
describe('mealsSlice', () => {
  it('handles fetchMeals.fulfilled correctly', () => {
    const initialState = { meals: [], loading: true };
    const action = {
      type: fetchMeals.fulfilled.type,
      payload: [{ id: '1', foodDescription: 'Pasta' }],
    };
    
    const newState = mealsReducer(initialState, action);
    expect(newState.meals).toHaveLength(1);
  });
});

// Test 4: Service layer (pure functions)
describe('mealApi', () => {
  it('constructs correct API request', async () => {
    const mockAxios = vi.spyOn(axiosInstance, 'get');
    
    await mealApi.getMeals('user-123', 1);
    
    expect(mockAxios).toHaveBeenCalledWith('/meals', {
      params: { userId: 'user-123', page: 1 },
    });
  });
});
```

### Key Benefits

✅ **Testability**: Each layer can be tested independently  
✅ **Flexibility**: Swap Redux for Context API without changing components  
✅ **Reusability**: Hooks can be used across multiple components  
✅ **Maintainability**: Clear separation makes bugs easy to locate  
✅ **Scalability**: New developers understand layer structure immediately  
✅ **Performance**: Memoized selectors prevent unnecessary re-renders

## Project Structure

### Directory Organization
```
src/frontend/
├── public/                          # Static assets
│   └── favicon.ico
├── src/
│   ├── components/                  # Reusable UI components
│   │   ├── Common/                  # Shared components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── __tests__/
│   │   ├── Auth/                    # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── __tests__/
│   │   ├── Meals/                   # Meal-related components
│   │   │   ├── MealCard.tsx
│   │   │   ├── MealUpload.tsx
│   │   │   ├── MealAnalysis.tsx
│   │   │   └── __tests__/
│   │   └── Settings/                # Settings components
│   │       ├── ProfileSettings.tsx
│   │       ├── NotificationPreferences.tsx
│   │       └── __tests__/
│   ├── pages/                       # Page components (routes)
│   │   ├── HomePage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── MealsPage.tsx
│   │   ├── AnalysisPage.tsx
│   │   ├── HistoryPage.tsx
│   │   └── SettingsPage.tsx
│   ├── hooks/                       # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useMeals.ts
│   │   ├── useNotifications.ts
│   │   └── useTelegram.ts
│   ├── services/                    # API and external service calls
│   │   ├── api/
│   │   │   ├── mealApi.ts
│   │   │   ├── userApi.ts
│   │   │   ├── authApi.ts
│   │   │   └── axiosConfig.ts
│   │   ├── telegram/
│   │   │   └── telegramService.ts
│   │   └── storage/
│   │       └── localStorageService.ts
│   ├── store/                       # Redux store configuration
│   │   ├── store.ts
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── mealsSlice.ts
│   │   │   ├── uiSlice.ts
│   │   │   └── notificationSlice.ts
│   │   └── selectors.ts
│   ├── types/                       # TypeScript types and interfaces
│   │   ├── index.ts
│   │   ├── models.ts
│   │   ├── api.ts
│   │   └── redux.ts
│   ├── utils/                       # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── errorHandler.ts
│   │   └── constants.ts
│   ├── themes/                      # Material-UI themes
│   │   ├── lightTheme.ts
│   │   ├── darkTheme.ts
│   │   └── themeProvider.tsx
│   ├── styles/                      # Global styles
│   │   ├── index.css
│   │   ├── variables.css
│   │   └── animations.css
│   ├── App.tsx                      # Root component
│   ├── main.tsx                     # Entry point
│   └── vite-env.d.ts               # Vite environment types
├── index.html                       # HTML entry point
├── tsconfig.json                    # TypeScript configuration
├── vite.config.ts                   # Vite build configuration
├── vitest.config.ts                 # Vitest test configuration
└── package.json                     # Dependencies and scripts
```

## Component Architecture

### Functional Component Pattern
```typescript
import React, { FC, useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { fetchMeals } from '@/store/slices/mealsSlice';

interface MealListProps {
  userId: string;
  onMealSelect?: (mealId: string) => void;
}

/**
 * MealList displays a paginated list of meals for the current user
 * with caching and infinite scroll support
 */
const MealList: FC<MealListProps> = ({ userId, onMealSelect }) => {
  const dispatch = useAppDispatch();
  const { items: meals, loading, error } = useAppSelector(state => state.meals);
  const [page, setPage] = useState(1);

  useEffect(() => {
    dispatch(fetchMeals({ userId, page }));
  }, [dispatch, userId, page]);

  if (loading && page === 1) return <LoadingSpinner />;
  if (error) return <ErrorAlert message={error} />;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {meals.map(meal => (
        <MealCard
          key={meal.id}
          meal={meal}
          onClick={() => onMealSelect?.(meal.id)}
        />
      ))}
    </Box>
  );
};

export default MealList;
```

### Component Composition Rules
- **Single Responsibility**: One component = one main purpose
- **Props First**: Props over context unless necessary for global state
- **Type Safety**: Always define Props interface
- **Memoization**: Use React.memo() only when needed (measure first)
- **Error Boundaries**: Wrap feature sections with error boundaries

### Component Size Guidelines
- Functional components: Keep <300 lines
- Hook logic: Extract custom hooks if >50 lines
- Complex render: Split into sub-components

## TypeScript Standards

### Type Definitions
```typescript
// types/models.ts - Define all domain models
export interface User {
  id: string;
  email: string;
  displayName: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Meal {
  id: string;
  userId: string;
  foodDescription: string;
  imageUrl: string;
  analysis?: MealAnalysis;
  notes?: string;
  createdAt: Date;
}

export interface MealAnalysis {
  id: string;
  mealId: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  micronutrients: Record<string, number>;
  recommendations: string[];
}

// types/api.ts - Define all API request/response types
export interface CreateMealRequest {
  foodDescription: string;
  base64Image: string;
  notes?: string;
}

export interface MealResponse {
  success: boolean;
  data: Meal;
  message: string;
  timestamp: string;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Array<{ field: string; message: string }>;
  };
  timestamp: string;
  requestId: string;
}
```

### Strict TypeScript Configuration
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## State Management (Redux)

### Redux Store Setup
```typescript
// store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import mealsReducer from './slices/mealsSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    meals: mealsReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Redux Slice Pattern
```typescript
// store/slices/mealsSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { mealApi } from '@/services/api/mealApi';
import { Meal } from '@/types/models';

interface MealsState {
  items: Meal[];
  loading: boolean;
  error: string | null;
  selectedMeal: Meal | null;
}

const initialState: MealsState = {
  items: [],
  loading: false,
  error: null,
  selectedMeal: null,
};

// Async thunks for API calls
export const fetchMeals = createAsyncThunk(
  'meals/fetchMeals',
  async ({ userId, page }: { userId: string; page: number }, { rejectWithValue }) => {
    try {
      const response = await mealApi.getMeals(userId, page);
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const createMeal = createAsyncThunk(
  'meals/createMeal',
  async (payload: any, { rejectWithValue }) => {
    try {
      const response = await mealApi.createMeal(payload);
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

const mealsSlice = createSlice({
  name: 'meals',
  initialState,
  reducers: {
    selectMeal: (state, action) => {
      state.selectedMeal = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMeals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMeals.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMeals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createMeal.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      });
  },
});

export const { selectMeal, clearError } = mealsSlice.actions;
export default mealsSlice.reducer;
```

### Redux Hooks
```typescript
// hooks/redux.ts
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from '@/store/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

## API Integration

### Axios Configuration
```typescript
// services/api/axiosConfig.ts
import axios, { AxiosError, AxiosResponse } from 'axios';
import { store } from '@/store/store';
import { logout } from '@/store/slices/authSlice';

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1',
  timeout: 10000,
});

// Request interceptor: Add auth token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Handle errors and refresh token
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - refresh token or logout
      store.dispatch(logout());
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

### API Service Pattern
```typescript
// services/api/mealApi.ts
import axiosInstance from './axiosConfig';
import { Meal, CreateMealRequest, MealResponse } from '@/types';

export const mealApi = {
  getMeals: async (userId: string, page: number = 1) => {
    return axiosInstance.get<MealResponse>(`/meals`, {
      params: { userId, page },
    });
  },

  getMealById: async (mealId: string) => {
    return axiosInstance.get<MealResponse>(`/meals/${mealId}`);
  },

  createMeal: async (payload: CreateMealRequest) => {
    return axiosInstance.post<MealResponse>('/meals', payload);
  },

  deleteMeal: async (mealId: string) => {
    return axiosInstance.delete(`/meals/${mealId}`);
  },

  updateMealNotes: async (mealId: string, notes: string) => {
    return axiosInstance.put(`/meals/${mealId}`, { notes });
  },
};
```

### Custom Hook for API Calls
```typescript
// hooks/useApi.ts
import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: AxiosError | null;
}

export function useApi<T>(
  apiCall: () => Promise<any>,
  immediate = true
): UseApiState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const response = await apiCall();
      setState({ data: response.data?.data, loading: false, error: null });
    } catch (error) {
      setState({ data: null, loading: false, error: error as AxiosError });
    }
  }, [apiCall]);

  useEffect(() => {
    if (immediate) execute();
  }, [execute, immediate]);

  return { ...state, refetch: execute };
}
```

## Custom Hooks

### Authentication Hook
```typescript
// hooks/useAuth.ts
import { useAppDispatch, useAppSelector } from './redux';
import { login, logout, register } from '@/store/slices/authSlice';

export function useAuth() {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, loading } = useAppSelector(state => state.auth);

  const handleLogin = useCallback(
    async (email: string, password: string) => {
      await dispatch(login({ email, password }));
    },
    [dispatch]
  );

  const handleLogout = useCallback(() => {
    dispatch(logout());
  }, [dispatch]);

  return {
    user,
    isAuthenticated,
    loading,
    login: handleLogin,
    logout: handleLogout,
  };
}
```

### Telegram Mini App Hook
```typescript
// hooks/useTelegram.ts
import { useEffect, useState } from 'react';
import TelegramBot from '@telegram-apps/sdk';

export function useTelegram() {
  const [webApp, setWebApp] = useState<any>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const app = (window as any).Telegram?.WebApp;
    if (app) {
      app.ready();
      setWebApp(app);
      setUser(app.initDataUnsafe?.user);
    }
  }, []);

  return {
    webApp,
    user,
    isReady: !!webApp,
    closeApp: () => webApp?.close(),
    expandApp: () => webApp?.expand(),
  };
}
```

## Material-UI Usage

### Theme Configuration
```typescript
// themes/lightTheme.ts
import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2E7D32', // Primary brand color
      light: '#66BB6A',
      dark: '#1B5E20',
    },
    secondary: {
      main: '#FFA726', // Secondary color
    },
    background: {
      default: '#FAFAFA',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2rem', fontWeight: 700 },
    h2: { fontSize: '1.75rem', fontWeight: 700 },
    body1: { fontSize: '1rem', lineHeight: 1.5 },
  },
  shape: {
    borderRadius: 8,
  },
});
```

### MUI Component Usage Pattern
```typescript
import { Box, Card, CardContent, Button, TextField, CircularProgress } from '@mui/material';

// Use sx prop for responsive styles
<Box sx={{
  display: 'flex',
  flexDirection: { xs: 'column', sm: 'row' },
  gap: 2,
  padding: { xs: 1, sm: 2, md: 3 },
}}>
  <TextField
    label="Food Description"
    variant="outlined"
    fullWidth
    error={!!errors.food}
    helperText={errors.food}
  />
  <Button
    variant="contained"
    color="primary"
    disabled={loading}
    endIcon={loading && <CircularProgress size={20} />}
  >
    Analyze
  </Button>
</Box>
```

## Performance Optimization

### Code Splitting
```typescript
import { lazy, Suspense } from 'react';

const MealsPage = lazy(() => import('@/pages/MealsPage'));
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));

export function AppRoutes() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/meals" element={<MealsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Suspense>
  );
}
```

### Component Memoization
```typescript
import { memo, useCallback } from 'react';

interface MealCardProps {
  meal: Meal;
  onSelect: (id: string) => void;
}

// Only re-render if props change
const MealCard = memo<MealCardProps>(({ meal, onSelect }) => {
  const handleClick = useCallback(() => onSelect(meal.id), [meal.id, onSelect]);
  
  return (
    <Card onClick={handleClick}>
      {/* Card content */}
    </Card>
  );
}, (prevProps, nextProps) => {
  // Custom comparison if needed
  return prevProps.meal.id === nextProps.meal.id;
});

export default MealCard;
```

### Image Optimization
```typescript
// Lazy load images, use WebP with fallback
<picture>
  <source srcSet={meal.imageUrl + '?format=webp&w=300'} type="image/webp" />
  <img
    src={meal.imageUrl + '?w=300'}
    alt={meal.foodDescription}
    loading="lazy"
    decoding="async"
  />
</picture>
```

## Form Handling

### React Hook Form Integration
```typescript
import { useForm, Controller, SubmitHandler } from 'react-hook-form';
import { TextField, Button } from '@mui/material';

interface CreateMealFormInputs {
  foodDescription: string;
  base64Image: string;
  notes?: string;
}

export function CreateMealForm() {
  const { control, handleSubmit, formState: { errors } } = useForm<CreateMealFormInputs>({
    defaultValues: {
      foodDescription: '',
      base64Image: '',
      notes: '',
    },
  });

  const onSubmit: SubmitHandler<CreateMealFormInputs> = async (data) => {
    await dispatch(createMeal(data));
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="foodDescription"
        control={control}
        rules={{
          required: 'Food description required',
          maxLength: { value: 1000, message: 'Max 1000 characters' },
        }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Food Description"
            multiline
            rows={3}
            error={!!errors.foodDescription}
            helperText={errors.foodDescription?.message}
          />
        )}
      />
      <Button type="submit">Upload Meal</Button>
    </form>
  );
}
```

## Error Handling

### Error Boundary Component
```typescript
import React, { ErrorInfo, ReactNode } from 'react';
import { Alert, Box, Button } from '@mui/material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 2 }}>
          <Alert severity="error">
            Something went wrong: {this.state.error?.message}
          </Alert>
          <Button onClick={() => this.setState({ hasError: false })}>
            Try again
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
```

## Testing Standards

### Component Testing with Vitest
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '@/store/store';
import MealCard from '@/components/Meals/MealCard';

describe('MealCard', () => {
  const mockMeal = {
    id: '1',
    foodDescription: 'Pizza',
    imageUrl: 'http://example.com/pizza.jpg',
    createdAt: new Date(),
  };

  it('should render meal information', () => {
    render(
      <Provider store={store}>
        <MealCard meal={mockMeal} onSelect={vi.fn()} />
      </Provider>
    );

    expect(screen.getByText('Pizza')).toBeInTheDocument();
  });

  it('should call onSelect when clicked', () => {
    const onSelect = vi.fn();
    render(
      <Provider store={store}>
        <MealCard meal={mockMeal} onSelect={onSelect} />
      </Provider>
    );

    fireEvent.click(screen.getByRole('article'));
    expect(onSelect).toHaveBeenCalledWith('1');
  });
});
```

### Hook Testing
```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useApi } from '@/hooks/useApi';

describe('useApi', () => {
  it('should fetch data successfully', async () => {
    const mockApi = vi.fn().mockResolvedValue({
      data: { data: { id: '1', name: 'Test' } },
    });

    const { result } = renderHook(() => useApi(mockApi));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toEqual({ id: '1', name: 'Test' });
    });
  });
});
```

## Build & Deployment

### Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'esnext',
    minify: 'terser',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],
          redux: ['redux', '@reduxjs/toolkit', 'react-redux'],
          mui: ['@mui/material', '@mui/icons-material'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
```

### Environment Variables
```bash
# .env.development
VITE_API_URL=http://localhost:5000/api/v1
VITE_TELEGRAM_BOT_TOKEN=xxx

# .env.production
VITE_API_URL=https://api.example.com/api/v1
VITE_TELEGRAM_BOT_TOKEN=xxx
```

## Accessibility (a11y)

### WCAG 2.1 AA Compliance
- All images have alt text
- Color contrast ratio ≥4.5:1 for normal text
- Interactive elements are keyboard accessible
- Focus indicators visible
- Semantic HTML structure
- ARIA labels where needed

```typescript
// ✅ Accessible button
<Button
  aria-label="Upload meal photo"
  onClick={handleUpload}
>
  <CameraIcon />
</Button>

// ✅ Accessible form
<TextField
  id="food-description"
  label="Food Description"
  aria-required="true"
  required
/>
```

## Development Workflow

### NPM Scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext ts,tsx",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write 'src/**/*.{ts,tsx,json,css}'"
  }
}
```

## Code Quality Checklist

Before submitting a PR:
- [ ] TypeScript strict mode passes (no `any`)
- [ ] All components have TypeScript types
- [ ] Unit tests written for business logic (>80% coverage)
- [ ] Component tests for user interactions
- [ ] No console errors/warnings
- [ ] Responsive on mobile, tablet, desktop
- [ ] Accessibility check passed (axe DevTools)
- [ ] Performance optimized (Lighthouse >90)
- [ ] Redux state properly normalized
- [ ] API errors handled gracefully
- [ ] Loading states implemented
- [ ] Form validation working

## Performance Targets

Target metrics for mobile-first Telegram Mini App:
- **First Contentful Paint (FCP):** <2 seconds
- **Largest Contentful Paint (LCP):** <2.5 seconds
- **Cumulative Layout Shift (CLS):** <0.1
- **Bundle Size:** <200KB (gzipped)
- **API Response:** <500ms (90th percentile)
- **Cache Hit Rate:** >80%

## Related Documentation
- `SYSTEM_ARCHITECTURE.md` - Overall system design
- `TECHNOLOGY_STACK.md` - Technology justifications
- `DOCKER_DEPLOYMENT_GUIDE.md` - Deployment procedures
- `full-stack-developer.prompt.md` - Story-by-story workflow
