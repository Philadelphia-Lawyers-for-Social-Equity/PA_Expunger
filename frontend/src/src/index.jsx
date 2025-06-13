import { createRoot } from 'react-dom/client';
import App from './App';
import { StrictMode } from 'react';
import './index.css';

const root = createRoot(document.getElementById('root'));
root.render(
    <StrictMode>
        <App />
    </StrictMode>
);
