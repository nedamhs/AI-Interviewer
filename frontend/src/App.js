import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomeView from './views/HomeView';
import EmployeeView from './views/EmployeeView';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<HomeView />} />
      <Route path="/employees" element={<EmployeeView />} />
    </Routes>
  </Router>
);

export default App;