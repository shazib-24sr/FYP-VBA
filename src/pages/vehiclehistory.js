import React, { useState, useEffect } from 'react';
import Navbar from '../components/ui/navbar';
import SidebarLayout from '../components/ui/sidebar';
import 'bootstrap/dist/css/bootstrap.min.css';

const VehicleHistoryPage = () => {
  const [vehicles, setVehicles] = useState([]);
  const [filteredVehicles, setFilteredVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedRows, setExpandedRows] = useState({});
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadVehicles = async () => {
    try {
      const res = await fetch('http://localhost:5000/vehicles');
      if (!res.ok) throw new Error('Failed to fetch vehicle list');
      const data = await res.json();
      setVehicles(data);
      setFilteredVehicles(data);
    } catch (error) {
      console.error('Error loading vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDetails = async (plate_number) => {
    if (expandedRows[plate_number]) {
      setExpandedRows((prev) => ({ ...prev, [plate_number]: null }));
      return;
    }

    try {
      const res = await fetch(`http://localhost:5000/vehicles/${plate_number}`);
      if (!res.ok) throw new Error('Failed to fetch vehicle details');
      const data = await res.json();
      setExpandedRows((prev) => ({ ...prev, [plate_number]: data }));
    } catch (error) {
      console.error('Error loading vehicle details:', error);
    }
  };

  const handleSearchChange = (e) => {
    const value = e.target.value.toUpperCase();
    setSearchTerm(value);
    const filtered = vehicles.filter((v) =>
      v.plate_number.toUpperCase().includes(value)
    );
    setFilteredVehicles(filtered);
  };

  return (
    <>
      <Navbar />
      <SidebarLayout>
        <div className="container py-4 bg-light min-vh-100">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h1 className="fw-bold">All Vehicle Violation Records</h1>
            <input
              type="text"
              className="form-control w-50"
              placeholder="Search by Plate Number..."
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </div>

          {loading ? (
            <p className="text-muted">Loading...</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-bordered table-striped table-hover">
                <thead className="table-dark">
                  <tr>
                    <th>Plate Number</th>
                    <th>Total Violations</th>
                    <th>Last Updated</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredVehicles.length > 0 ? (
                    filteredVehicles.map((vehicle) => (
                      <React.Fragment key={vehicle.plate_number}>
                        <tr>
                          <td>{vehicle.plate_number}</td>
                          <td>
                            <span
                              className={`badge ${vehicle.total_violations > 0 ? 'bg-danger' : 'bg-secondary'}`}
                            >
                              {vehicle.total_violations}
                            </span>
                          </td>
                          <td>{new Date(vehicle.last_updated).toLocaleString()}</td>
                          <td>
                            <button
                              className="btn btn-sm btn-primary"
                              onClick={() => toggleDetails(vehicle.plate_number)}
                            >
                              {expandedRows[vehicle.plate_number] ? 'Hide Details' : 'View Details'}
                            </button>
                          </td>
                        </tr>

                        {expandedRows[vehicle.plate_number] && (
                          <tr>
                            <td colSpan="4">
                              <h5 className="fw-bold">Violation Details:</h5>
                              {expandedRows[vehicle.plate_number].violations.length > 0 ? (
                                <div className="table-responsive">
                                  <table className="table table-sm table-bordered">
                                    <thead className="table-light">
                                      <tr>
                                        <th>Violation Type</th>
                                        <th>Date & Time</th>
                                        <th>Image</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {expandedRows[vehicle.plate_number].violations.map((violation, idx) => (
                                        <tr key={idx}>
                                          <td>{violation.violation_type}</td>
                                          <td>{new Date(violation.video_datetime).toLocaleString()}</td>
                                          <td>
                                            <img
                                              src={`data:image/jpeg;base64,${violation.image_data}`}
                                              alt="violation"
                                              style={{ width: '100px', height: 'auto' }}
                                            />
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              ) : (
                                <p className="text-muted">No violations found for this vehicle.</p>
                              )}
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="text-center text-muted">
                        No vehicle records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </SidebarLayout>
    </>
  );
};

export default VehicleHistoryPage;
