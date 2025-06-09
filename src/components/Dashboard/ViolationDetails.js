import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
const ViolationDetails = ({ violations, capturedSpots, pieChartData }) => (
  <div className="card shadow-sm p-4">
    <div className="card-body">
      <h5 className="card-title fw-bold mb-2">Violations: {violations}</h5>
      <p className="card-text small">Captured at Spots: {capturedSpots.join(' - ')}</p>
      <div className="mt-3">
        <p className="fw-medium mb-2">Violated Vehicles Detail</p>
        <ul className="ps-4">
          {pieChartData.map((d) => (
            <li key={d.label}>{d.value}% {d.label}</li>
          ))}
        </ul>
      </div>
    </div>
  </div>
);

export default ViolationDetails;
