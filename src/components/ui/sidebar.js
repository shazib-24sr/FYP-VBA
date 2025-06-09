import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const SidebarLayout = ({ children }) => {
  const navigate = useNavigate();

  const handleSignOut = () => {
    
    navigate('/');
  };

  return (
    <div className="d-flex" style={{ minHeight: '100vh' }}>
      <div className="bg-dark text-white p-4" style={{ width: '220px' }}>
        <h4 className="mb-4">Menu</h4>
        <ul className="nav flex-column">
          <li className="nav-item mb-2">
            <Link className="nav-link text-white" to="/dashboard">🏠 Home</Link>
          </li>
          <li className="nav-item mb-2">
            <Link className="nav-link text-white" to="/upload">📤 Upload Videos</Link>
          </li>
          <li className="nav-item mb-2">
            <Link className="nav-link text-white" to="/search">🔍 Search Vehicle</Link>
          </li> 
          <li className="nav-item mb-2">
            <Link className="nav-link text-white" to="/vehiclehistory">🛢️ Vehicle History</Link>
          </li>   

          <li className="nav-item mb-2">
            <Link className="nav-link text-white" to="/chat">💬 Ask Questions</Link>
          </li>
          <li className="nav-item mb-2">
            <Link className="nav-link text-white " to="/">🚪 Sign Out</Link>
          </li>
         
        </ul>
      </div>
      <div className="flex-grow-1 p-4 bg-light">
        {children}
      </div>
    </div>
  );
};

export default SidebarLayout;
