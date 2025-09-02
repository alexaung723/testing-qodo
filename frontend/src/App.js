import React, { useRef, useEffect, useState } from 'react';
import axios from 'axios';

const GAME_WIDTH = 400;
const GAME_HEIGHT = 600;
const BIRD_SIZE = 30;
const GRAVITY = 2;
const JUMP_HEIGHT = 50;
const PIPE_WIDTH = 60;
const PIPE_GAP = 150;

function getRandomPipeY() {
  return Math.floor(Math.random() * (GAME_HEIGHT - PIPE_GAP - 100)) + 50;
}

function App() {
  const [birdY, setBirdY] = useState(GAME_HEIGHT / 2);
  const [pipes, setPipes] = useState([
    { x: GAME_WIDTH, y: getRandomPipeY() },
  ]);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [highScores, setHighScores] = useState([]);
  const [name, setName] = useState('');
  const gameRef = useRef();
  const velocity = useRef(0);

  useEffect(() => {
    axios.get('http://localhost:5000/api/highscores').then(res => {
      setHighScores(res.data);
    });
  }, [gameOver]);

  useEffect(() => {
    if (gameOver) return;
    const handleSpace = (e) => {
      if (e.code === 'Space') {
        velocity.current = -JUMP_HEIGHT;
      }
    };
    window.addEventListener('keydown', handleSpace);
    return () => window.removeEventListener('keydown', handleSpace);
  }, [gameOver]);

  useEffect(() => {
    if (gameOver) return;
    const interval = setInterval(() => {
      setBirdY(prev => {
        let nextY = prev + velocity.current + GRAVITY;
        velocity.current += GRAVITY;
        return Math.max(0, Math.min(GAME_HEIGHT - BIRD_SIZE, nextY));
      });
      setPipes(prev => {
        let newPipes = prev.map(pipe => ({ ...pipe, x: pipe.x - 4 }));
        if (newPipes[0].x < -PIPE_WIDTH) {
          newPipes.shift();
          newPipes.push({ x: GAME_WIDTH, y: getRandomPipeY() });
          setScore(s => s + 1);
        }
        return newPipes;
      });
    }, 20);
    return () => clearInterval(interval);
  }, [gameOver]);

  useEffect(() => {
    if (gameOver) return;
    // Collision detection
    const birdBox = {
      x: 50,
      y: birdY,
      w: BIRD_SIZE,
      h: BIRD_SIZE,
    };
    for (let pipe of pipes) {
      // Top pipe
      if (
        birdBox.x + birdBox.w > pipe.x &&
        birdBox.x < pipe.x + PIPE_WIDTH &&
        birdBox.y < pipe.y
      ) {
        setGameOver(true);
      }
      // Bottom pipe
      if (
        birdBox.x + birdBox.w > pipe.x &&
        birdBox.x < pipe.x + PIPE_WIDTH &&
        birdBox.y + birdBox.h > pipe.y + PIPE_GAP
      ) {
        setGameOver(true);
      }
    }
    // Ground or ceiling
    if (birdY <= 0 || birdY >= GAME_HEIGHT - BIRD_SIZE) {
      setGameOver(true);
    }
  }, [birdY, pipes, gameOver]);

  const handleRestart = () => {
    setBirdY(GAME_HEIGHT / 2);
    setPipes([{ x: GAME_WIDTH, y: getRandomPipeY() }]);
    setScore(0);
    setGameOver(false);
    velocity.current = 0;
  };

  const handleSubmitScore = async () => {
    if (!name) return;
    await axios.post('http://localhost:5000/api/highscores', { name, score });
    setName('');
    setGameOver(false);
    handleRestart();
  };

  return (
    <div style={{ width: GAME_WIDTH, height: GAME_HEIGHT, margin: '40px auto', position: 'relative', background: '#87ceeb', overflow: 'hidden', borderRadius: 10, boxShadow: '0 0 20px #333' }}>
      {/* Bird */}
      <div style={{ position: 'absolute', left: 50, top: birdY, width: BIRD_SIZE, height: BIRD_SIZE, background: 'yellow', borderRadius: '50%', border: '2px solid #333' }} />
      {/* Pipes */}
      {pipes.map((pipe, i) => (
        <React.Fragment key={i}>
          {/* Top pipe */}
          <div style={{ position: 'absolute', left: pipe.x, top: 0, width: PIPE_WIDTH, height: pipe.y, background: 'green', border: '2px solid #333' }} />
          {/* Bottom pipe */}
          <div style={{ position: 'absolute', left: pipe.x, top: pipe.y + PIPE_GAP, width: PIPE_WIDTH, height: GAME_HEIGHT - pipe.y - PIPE_GAP, background: 'green', border: '2px solid #333' }} />
        </React.Fragment>
      ))}
      {/* Score */}
      <div style={{ position: 'absolute', top: 10, left: 10, fontSize: 24, color: '#333', fontWeight: 'bold' }}>Score: {score}</div>
      {/* Game Over */}
      {gameOver && (
        <div style={{ position: 'absolute', top: GAME_HEIGHT / 2 - 80, left: 0, width: '100%', textAlign: 'center', color: '#333' }}>
          <h2>Game Over!</h2>
          <div>Final Score: {score}</div>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" style={{ marginTop: 10 }} />
          <button onClick={handleSubmitScore} style={{ marginLeft: 10 }}>Submit Score</button>
          <button onClick={handleRestart} style={{ marginLeft: 10 }}>Restart</button>
          <div style={{ marginTop: 20 }}>
            <h3>High Scores</h3>
            <ol>
              {highScores.map((hs, i) => (
                <li key={i}>{hs.name}: {hs.score}</li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;