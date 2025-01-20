import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import EmployeeView from '../views/EmployeeView';
import HomeView from '../views/HomeView';

function App() {

    return (
        <Router>
            <Routes>
                <Route path="/" element={
                    <HomeView />
                } />
                <Route path="/employees" element={
                    <EmployeeView />
                } />
            </Routes>
        </Router>
    );
};

export default App;