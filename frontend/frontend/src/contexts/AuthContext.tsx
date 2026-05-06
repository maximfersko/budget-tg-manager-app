import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import keycloak, { keycloakConfig } from '../config/keycloak';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  loginWithGoogle: () => void;
  loginWithGithub: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    try {
      keycloak.logout({
        redirectUri: window.location.origin,
      });
    } catch (error) {
      console.warn('Keycloak logout failed', error);
    }
    setIsAuthenticated(false);
    setUser(null);
  }, []);

  const loadUserProfile = async () => {
    try {
      const profile = await keycloak.loadUserProfile();
      setUser({
        id: profile.id,
        email: profile.email,
        firstName: profile.firstName,
        lastName: profile.lastName,
        username: profile.username,
      });
    } catch (error) {
      console.error('Failed to load user profile', error);
    }
  };

  useEffect(() => {
    const initKeycloak = async () => {
      try {
        const authenticated = await keycloak.init({
          onLoad: 'check-sso',
          silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
          pkceMethod: 'S256',
          checkLoginIframe: false,
        }).catch((error: unknown) => {
          console.warn('Keycloak initialization failed, continuing without authentication', error);
          return false;
        });

        setIsAuthenticated(authenticated || false);

        if (authenticated) {
          await loadUserProfile().catch((error) => {
            console.warn('Failed to load user profile', error);
          });
        }

        keycloak.onTokenExpired = () => {
          keycloak.updateToken(30).catch(() => {
            logout();
          });
        };
      } catch (error) {
        console.error('Failed to initialize Keycloak', error);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initKeycloak();
  }, [logout]);

  const login = async (email: string, password: string) => {
    try {
      if (keycloak.authenticated || isAuthenticated) {
        return;
      }

      const response = await fetch(
        `${keycloakConfig.url}/realms/${keycloakConfig.realm}/protocol/openid-connect/token`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            grant_type: 'password',
            client_id: keycloakConfig.clientId,
            username: email,
            password: password,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error_description: 'Login failed' }));
        throw new Error(error.error_description || 'Invalid credentials');
      }

      const data = await response.json();
      
      await keycloak.init({
        token: data.access_token,
        refreshToken: data.refresh_token,
        onLoad: 'check-sso',
        checkLoginIframe: false,
      });

      setIsAuthenticated(true);
      await loadUserProfile();
    } catch (error: any) {
      setIsAuthenticated(false);
      throw error;
    }
  };

  const register = async (email: string, password: string, firstName?: string, lastName?: string) => {
    try {
      if (keycloak.authenticated || isAuthenticated) {
        return;
      }

      const adminTokenResponse = await fetch(
        `${keycloakConfig.url}/realms/master/protocol/openid-connect/token`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            grant_type: 'password',
            client_id: 'admin-cli',
            username: 'admin',
            password: 'admin',
          }),
        }
      );

      if (!adminTokenResponse.ok) {
        throw new Error('Registration service unavailable');
      }

      const adminTokenData = await adminTokenResponse.json();
      const adminToken = adminTokenData.access_token;

      const createUserResponse = await fetch(
        `${keycloakConfig.url}/admin/realms/${keycloakConfig.realm}/users`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${adminToken}`,
          },
          body: JSON.stringify({
            email,
            username: email,
            firstName: firstName || '',
            lastName: lastName || '',
            enabled: true,
            emailVerified: false,
            credentials: [
              {
                type: 'password',
                value: password,
                temporary: false,
              },
            ],
          }),
        }
      );

      if (!createUserResponse.ok) {
        const error = await createUserResponse.json().catch(() => ({ errorMessage: 'Registration failed' }));
        const errorMessage = error.errorMessage || error.error || 'Registration failed';
        
        if (errorMessage.includes('exists') || errorMessage.includes('duplicate')) {
          throw new Error('User with this email already exists');
        }
        
        throw new Error(errorMessage);
      }

      await login(email, password);
    } catch (error: any) {
      if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError') || error.message.includes('CORS'))) {
        throw new Error('Unable to connect to authentication server. Please check your connection and try again.');
      }
      throw error;
    }
  };

  const loginWithGoogle = () => {
    try {
      if (keycloak.authenticated || isAuthenticated) {
        return;
      }

      const width = 500;
      const height = 600;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      const popup = window.open(
        `${keycloakConfig.url}/realms/${keycloakConfig.realm}/protocol/openid-connect/auth?client_id=${keycloakConfig.clientId}&redirect_uri=${encodeURIComponent(window.location.origin + '/dashboard')}&response_type=code&scope=openid profile email&kc_idp_hint=google`,
        'keycloak-login',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      if (!popup) {
        throw new Error('Popup blocked');
      }

      const checkPopup = setInterval(() => {
        try {
          if (popup.closed) {
            clearInterval(checkPopup);
            return;
          }

          if (popup.location.href.includes('/dashboard')) {
            clearInterval(checkPopup);
            popup.close();
            window.location.reload();
          }
        } catch (e) {
        }
      }, 500);
    } catch (error) {
      console.warn('Keycloak login failed', error);
    }
  };

  const loginWithGithub = () => {
    try {
      if (keycloak.authenticated || isAuthenticated) {
        return;
      }

      const width = 500;
      const height = 600;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      const popup = window.open(
        `${keycloakConfig.url}/realms/${keycloakConfig.realm}/protocol/openid-connect/auth?client_id=${keycloakConfig.clientId}&redirect_uri=${encodeURIComponent(window.location.origin + '/dashboard')}&response_type=code&scope=openid profile email&kc_idp_hint=github`,
        'keycloak-login',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      if (!popup) {
        throw new Error('Popup blocked');
      }

      const checkPopup = setInterval(() => {
        try {
          if (popup.closed) {
            clearInterval(checkPopup);
            return;
          }

          if (popup.location.href.includes('/dashboard')) {
            clearInterval(checkPopup);
            popup.close();
            window.location.reload();
          }
        } catch (e) {
        }
      }, 500);
    } catch (error) {
      console.warn('Keycloak login failed', error);
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    register,
    loginWithGoogle,
    loginWithGithub,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

