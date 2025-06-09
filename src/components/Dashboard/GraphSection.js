import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, LineChart, Line, CartesianGrid, ResponsiveContainer } from 'recharts';
import 'bootstrap/dist/css/bootstrap.min.css';
const GraphSection = ({ specificViolations, totalViolationsGraph }) => {
  const specificData = Object.entries(specificViolations).map(([spot, val], i) => ({
    name: `GT Road Wazirabad Location ${i + 1}`,
    value: val,
  }));

  return (
    <div className="row g-4">
      <div className="col-md-6">
        <div className="card shadow-sm p-3 bg-white rounded">
          <h5 className="text-center mb-3">Violations by Spot</h5>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={specificData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#007BFF" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="col-md-6">
        <div className="card shadow-sm p-3 bg-white rounded">
          <h5 className="text-center mb-3">Total Violations Over Time</h5>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={totalViolationsGraph}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="spot" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#00BFFF" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default GraphSection;