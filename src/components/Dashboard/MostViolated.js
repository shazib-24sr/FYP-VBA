import React from 'react';
import Card, { CardContent } from '../ui/Card';
import 'bootstrap/dist/css/bootstrap.min.css';

const MostViolated = ({ count, type }) => (
  <div className="card shadow-sm p-4">
    <div className="card-body">
      <p className="card-text fw-medium">Most Violation Count: {count}</p>
      <p className="text-primary fw-bold fs-4 mt-2">
        Most Violations<br />
        {type}
      </p>
    </div>
  </div>
);

export default MostViolated;
