import { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

function App() {
  const [view, setView] = useState('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      setView('dashboard');
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setView('login');
  };

  if (view === 'dashboard' && isAuthenticated) {
    return <Dashboard onLogout={handleLogout} />;
  }

  if (view === 'register') {
    return (
      <Register
        onSuccess={handleLoginSuccess}
        onSwitchToLogin={() => setView('login')}
      />
    );
  }

  return (
    <Login
      onSuccess={handleLoginSuccess}
      onSwitchToRegister={() => setView('register')}
    />
  );
}

export default App;
