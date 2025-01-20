import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App';

const rootContainer = document.getElementById('react-root');
const root = createRoot(rootContainer); 
root.render(<App />);