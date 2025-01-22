import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import HomeView from '../views/HomeView';

function App() {

    return (
        <Router>
            <Routes>
                <Route path="/" element={
                    <HomeView />
                } />
            </Routes>
        </Router>
    );
};

export default App;