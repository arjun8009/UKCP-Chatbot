import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import ChatbotCard from './Components/ChatbotCard';
import SignInPage from './Components/SignInPage';
import SignUpPage from './Components/SignUpage';
import './App.css';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<SignInPage />} />
          <Route path="/UI" element={<ChatbotCard />} />
          <Route path="/signup" element={<SignUpPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;