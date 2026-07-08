import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

function OAuthCallback() {
  const [status, setStatus] = React.useState('Processing...');

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const error = params.get('error');

    if (error) {
      setStatus('Authentication failed: ' + error);
      return;
    }

    if (!code) {
      setStatus('No authorization code received');
      return;
    }

    fetch('/api/auth/google/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem('nova_token', data.access_token);
          localStorage.setItem('nova_user', JSON.stringify({ id: data.user_id }));
          window.location.href = '/';
        } else {
          setStatus('Authentication failed: ' + (data.detail || 'Unknown error'));
        }
      })
      .catch(() => {
        setStatus('Failed to connect to auth server');
      });
  }, []);

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', fontFamily: 'system-ui' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>NotebookLM Portal</div>
        <div style={{ color: '#64748b' }}>{status}</div>
      </div>
    </div>
  );
}

const path = window.location.pathname;
const Root = path === '/auth/callback' ? OAuthCallback : App;

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)
