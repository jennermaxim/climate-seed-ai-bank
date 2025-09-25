export interface User {
  id: number;
  email: string;
  full_name: string;
  user_type: 'farmer' | 'admin' | 'policy_maker';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  private tokenKey = 'auth_token';
  private userKey = 'auth_user';

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  getUser(): User | null {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  setUser(user: User): void {
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    
    // Store token and user info
    this.setToken(data.access_token);
    
    // Get user info
    const userResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${data.access_token}`,
      },
    });
    
    if (userResponse.ok) {
      const user = await userResponse.json();
      this.setUser(user);
      return { ...data, user };
    }

    return data;
  }

  async register(userData: {
    email: string;
    password: string;
    full_name: string;
    user_type: string;
  }): Promise<User> {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    return response.json();
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();