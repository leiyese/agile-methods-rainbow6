import React, { useState, useEffect } from 'react';
import './App.css';

// Use environment variable for API URL, fallback to relative path
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

function App() {
  const [items, setItems] = useState([]);
  const [newItemName, setNewItemName] = useState('');
  const [status, setStatus] = useState('Disconnected');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
    fetchItems();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data.status === 'ok' ? 'Connected' : 'Error');
      } else {
        setStatus('Error');
      }
    } catch (err) {
      setStatus('Disconnected');
      setError('Cannot connect to backend. Make sure Flask server is running on port 5000.');
    }
  };

  const fetchItems = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/items`);
      if (response.ok) {
        const data = await response.json();
        setItems(data.items);
      } else {
        setError('Failed to fetch items');
      }
    } catch (err) {
      setError('Cannot fetch items from backend');
    }
    setLoading(false);
  };

  const addItem = async (e) => {
    e.preventDefault();
    if (!newItemName.trim()) return;

    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newItemName.trim() }),
      });

      if (response.ok) {
        const newItem = await response.json();
        setItems([...items, newItem]);
        setNewItemName('');
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to add item');
      }
    } catch (err) {
      setError('Cannot add item - backend connection failed');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React + Flask Demo</h1>
        <div className={`status ${status.toLowerCase()}`}>
          Backend Status: <strong>{status}</strong>
        </div>
      </header>

      <main className="App-main">
        {error && <div className="error">{error}</div>}
        
        <section className="add-item-section">
          <h2>Add New Item</h2>
          <form onSubmit={addItem} className="add-item-form">
            <input
              type="text"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              placeholder="Enter item name"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !newItemName.trim()}>
              {loading ? 'Adding...' : 'Add Item'}
            </button>
          </form>
        </section>

        <section className="items-section">
          <div className="items-header">
            <h2>Items ({items.length})</h2>
            <button onClick={fetchItems} disabled={loading}>
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
          
          {items.length === 0 ? (
            <p className="no-items">No items yet. Add one above!</p>
          ) : (
            <ul className="items-list">
              {items.map((item) => (
                <li key={item.id} className="item">
                  <span className="item-id">#{item.id}</span>
                  <span className="item-name">{item.name}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
