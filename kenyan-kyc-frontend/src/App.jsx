import { useState, useEffect } from 'react';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

function BackToHome({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="fixed top-4 left-4 z-10 px-3 py-2 rounded-lg bg-white/90 text-kenya-green text-sm font-semibold shadow hover:bg-white"
    >
      ← About Uwezo KYC
    </button>
  );
}

function App() {
  const [view, setView] = useState('home');
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
    setView('home');
  };

  if (view === 'dashboard' && isAuthenticated) {
    return <Dashboard onLogout={handleLogout} />;
  }

  if (view === 'register') {
    return (
      <>
        <BackToHome onClick={() => setView('home')} />
        <Register
          onSuccess={handleLoginSuccess}
          onSwitchToLogin={() => setView('login')}
        />
      </>
    );
  }

  if (view === 'login') {
    return (
      <>
        <BackToHome onClick={() => setView('home')} />
        <Login
          onSuccess={handleLoginSuccess}
          onSwitchToRegister={() => setView('register')}
        />
      </>
    );
  }

  return (
    <Home
      onSignIn={() => setView('login')}
      onRegister={() => setView('register')}
    />
  );
}

export default App;