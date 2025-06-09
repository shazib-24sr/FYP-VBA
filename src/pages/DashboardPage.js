import React, { useEffect, useState } from 'react';
import VehicleCard from '../components/Dashboard/VehicleCard';
import ViolationDetails from '../components/Dashboard/ViolationDetails';
import MostViolated from '../components/Dashboard/MostViolated';
import GraphSection from '../components/Dashboard/GraphSection';
import Navbar from "../components/ui/navbar";
import SidebarLayout from '../components/ui/sidebar';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';


const DashboardPage = () => {
  const navigate = useNavigate();

  const handleViewViolations = () => {
    navigate('/violations');  // Navigate to the violations page
  };

  const [dashboardData, setDashboardData] = useState({
    totalVehicles: 0,
    totalViolations: 0,
    mostViolatedVehicle: "N/A",
    mostViolationCount: 0,
    mostViolationsType: "N/A",
    violations: 0,
    capturedSpots: [],
    specificViolations: {},
    pieChartData: [],
    totalViolationsGraph: []
  });

  useEffect(() => {
    fetch('http://localhost:5000/dashboard-data')
      .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
      })
      .then(data => {
        setDashboardData(data);
      })
      .catch(error => {
        console.error('Error fetching dashboard data:', error);
      });
  }, []);

  return (
    <>
      <Navbar />
      <SidebarLayout>
        <div className="container py-4 bg-light min-vh-100">
          <h1 className="text-center fw-bold mb-4">Vehicle Behaviour Analysis</h1>

          <div className="row g-4 mb-4">
            <div className="col-md-4">
              <VehicleCard title="Total Vehicles Count" value={dashboardData.totalVehicles} />
            </div>
            <div className="col-md-4">
              <VehicleCard title="Total Violations" value={dashboardData.totalViolations} bgColor="bg-primary" textColor="text-white" />
            </div>
            <div className="col-md-4">
              <VehicleCard title="Most Violated Vehicle" value={dashboardData.mostViolatedVehicle} bgColor="bg-primary text-white" />
            </div>
          </div>

          <div className="row g-4 mb-4">
            <div className="col-md-6">
              <ViolationDetails
                violations={dashboardData.violations}
                capturedSpots={dashboardData.capturedSpots}
                pieChartData={dashboardData.pieChartData}
              />
            </div>
            <div className="col-md-6">
              <MostViolated 
                count={dashboardData.mostViolationCount} 
                type={dashboardData.mostViolationsType} 
              />
            </div>
          </div>

          <div className="mb-4">
            <GraphSection
              specificViolations={dashboardData.specificViolations}
              totalViolationsGraph={dashboardData.totalViolationsGraph}
            />
          </div>

          <div className="text-center">
            <button className="btn btn-primary" onClick={handleViewViolations}>
              View Violated Frames
            </button>
          </div>
        </div>
      </SidebarLayout>
    </>
  );
};

export default DashboardPage;
