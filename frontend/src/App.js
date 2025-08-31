import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
    const [count, setCount] = useState(0);

    const incrementCount = async () => {
        const response = await fetch('http://localhost:5000/increment', {
            method: 'POST',
        });
        if (response.ok) {
            const data = await response.json();
            setCount(data.count);
        }
    };

    useEffect(() => {
        const fetchCount = async () => {
            const response = await fetch('http://localhost:5000/count');
            if (response.ok) {
                const data = await response.json();
                setCount(data.count);
            }
        };
        fetchCount();
    }, []);

    return (
        <div className="App" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <button onClick={incrementCount} style={{ fontSize: '24px', padding: '10px 20px' }}>
                Count: {count}
            </button>
        </div>
    );
}

export default App;