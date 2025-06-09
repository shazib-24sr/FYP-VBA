import React, { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';
import 'bootstrap/dist/css/bootstrap.min.css';
import axios from 'axios';

const SearchDetails = ({ summary, violations, capturedSpots, pieChartData, vehicleId }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [violationFrames, setViolationFrames] = useState({});

  console.log("vehicleId:", vehicleId);
  console.log("violations:", violations);

  useEffect(() => {
    if (vehicleId !== undefined && violations && violations.length > 0) {
      console.log("Fetching frames for violations:", violations);
      violations.forEach(({ violationType }) => {
        if (violationType) {
          console.log(`Fetching frames for violationType: ${violationType}`);
          axios
            .get(`http://localhost:5000/viewViolatedFrameByVehicle/${encodeURIComponent(violationType)}/${vehicleId}`)
            .then((response) => {
              setViolationFrames((prev) => ({ ...prev, [violationType]: response.data }));
              console.log(`Frames for ${violationType}:`, response.data);
            })
            .catch((error) => {
              console.error(`Error fetching frames for ${violationType}:`, error);
              setViolationFrames((prev) => ({ ...prev, [violationType]: [] }));
            });
        }
      });
    } else {
      console.log("No vehicleId or violations to fetch frames");
    }
  }, [violations, vehicleId]);

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    if (pieChartData && pieChartData.length > 0) {
      const ctx = chartRef.current.getContext('2d');
      const labels = pieChartData.map((item) => item.type);
      const values = pieChartData.map((item) => item.count);

      chartInstance.current = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [
            {
              data: values,
              backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)',
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Violation Breakdown' },
          },
        },
      });
    }
  }, [pieChartData]);

  return (
    <div className="container">
      <h2 className="text-center my-4">Journey Summary</h2>
      {summary && Object.keys(summary).length > 0 ? (
        <div className="card mb-4 shadow-sm">
          <div className="card-body">
            <p>
              <strong>Total Distance:</strong> {summary.total_distance?.toFixed(2)} meters
            </p>
            <p>
              <strong>Average Speed:</strong> {summary.avg_speed?.toFixed(2)} km/h
            </p>
            <p>
              <strong>Total Violations:</strong> {summary.total_violations}
            </p>
          </div>
        </div>
      ) : (
        <p className="text-muted text-center">No summary data available.</p>
      )}

      <h2 className="text-center my-4">Violation Details</h2>
      {violations && violations.length > 0 ? (
        violations.map((violation, index) => (
          <div key={index} className="card mb-3 shadow-sm">
            <div className="card-body">
              {violation.violationType && <p><strong>Violation Type:</strong> {violation.violationType}</p>}

              <div className="d-flex flex-wrap">
                {violationFrames[violation.violationType]?.length > 0 ? (
                  violationFrames[violation.violationType].map((frameUrl, i) => (
                    <img
                      key={i}
                      src={`http://localhost:5000${frameUrl}`}
                      alt={`Frame ${i + 1} for ${violation.violationType}`}
                      style={{ width: '150px', height: 'auto', marginRight: '10px', marginBottom: '10px' }}
                    />
                  ))
                ) : (
                  <p>No frames available.</p>
                )}
              </div>
            </div>
          </div>
        ))
      ) : (
        <p className="text-muted">No violations found.</p>
      )}

      {pieChartData && pieChartData.length > 0 && (
        <div className="my-5 mx-auto" style={{ width: '350px', height: '300px' }}>
          <h4 className="text-center mb-3">Violation Summary</h4>
          <canvas ref={chartRef} />
        </div>
      )}
    </div>
  );
};

export default SearchDetails;
