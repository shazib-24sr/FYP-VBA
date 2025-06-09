import React from 'react';
import Card, { CardContent } from '../ui/Card';
import 'bootstrap/dist/css/bootstrap.min.css';


const VehicleCard = ({ title, value, bgColor = 'bg-light', textColor = 'text-dark' }) => (
  <div className={`card shadow-sm text-center ${bgColor} ${textColor}`}>
    <div className="card-body py-4">
      <p className="h6 fw-medium">{title}</p>
      <h2 className="display-6 fw-bold">{value}</h2>
    </div>
  </div>
);

export default VehicleCard;