import React, { useState } from 'react';
import Navbar from "../components/ui/navbar";
import SidebarLayout from '../components/ui/sidebar';
import 'bootstrap/dist/css/bootstrap.min.css';
import SearchDetails from '../components/Dashboard/searchDetails';

const SearchPage = () => {
  const [vehicleId, setVehicleId] = useState('');
  const [loading, setLoading] = useState(false);
  const [violationsData, setViolationsData] = useState(null);
  const [error, setError] = useState(null);
    
  const handleSearch = async () => {
    if (!vehicleId.trim()) {
      setError('Please enter a vehicle ID');
      setViolationsData(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/violations?vehicleId=${encodeURIComponent(vehicleId)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch violations for this vehicle');
      }
      const data = await response.json();
      setViolationsData(data);
    } catch (err) {
      setError(err.message);
      setViolationsData(null);
    }
    setLoading(false);
  };

  return (
    <>
      <Navbar />
      <SidebarLayout>
        <div className="container py-4 bg-light min-vh-100">
          <h1 className="text-center fw-bold mb-4">Search Vehicle Violations</h1>

          <div className="row justify-content-center mb-4">
            <div className="col-md-6">
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter Vehicle ID or Plate Number"
                  value={vehicleId}
                  onChange={(e) => setVehicleId(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(); }}
                />
                <button
                  className="btn btn-primary"
                  type="button"
                  onClick={handleSearch}
                  disabled={loading}
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
              {error && <div className="text-danger mt-2">{error}</div>}
            </div>
          </div>

          {violationsData ? (
            violationsData.violations && violationsData.violations.length > 0 ? (
              <SearchDetails
                summary={violationsData.summary || {}}
                violations={violationsData.violations}
                capturedSpots={violationsData.capturedSpots || []}
                pieChartData={violationsData.pieChartData || []}
                vehicleId={vehicleId} 
              />
            ) : (
              <p className="text-center text-muted">No data found for vehicle "{vehicleId}"</p>
            )
          ) : (
            <p className="text-center text-muted">Search for a vehicle to see its violations.</p>
          )}
        </div>
      </SidebarLayout>
    </>
  );
};

export default SearchPage;
