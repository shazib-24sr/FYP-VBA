import React, { useState, useEffect } from 'react';
import Navbar  from '../ui/navbar';
const VIOLATION_TYPES = ['overspeeding', 'wrongway', 'abruptLaneChange'];

const ViewViolatedFrame = () => {
  const [frames, setFrames] = useState({
    overspeeding: [],
    wrongway: [],
    abruptLaneChange: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFrames = async () => {
      setLoading(true);
      try {
        const newFrames = {};
        for (const type of VIOLATION_TYPES) {
          const response = await fetch(`http://localhost:5000/viewViolatedFrame/${type}`);
          const data = await response.json();
          newFrames[type] = data;
        }
        setFrames(newFrames);
      } catch (error) {
        console.error('Error fetching violation frames:', error);
      }
      setLoading(false);
    };

    fetchFrames();
  }, []);

  if (loading) return <p>Loading violation frames...</p>;

  return ( <>    <Navbar/>
    <div className="container text-center mt-4">

      {/* Video player
      <div className="mb-5">
        <h3>Processed Video</h3>
        <video width="640" height="360" controls>
          <source src="http://localhost:5000/video/output_0011.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div> */}
      {/* Video players */}
<div className="mb-5">
  <h3>Processed Videos</h3>

  <div className="d-flex flex-wrap justify-content-center gap-4">
  <div>
    <h5>Output 1</h5>
    <video width="540" height="380" autoPlay loop muted playsInline>
      <source src="http://localhost:5000/video/output_1.mp4" type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  </div>

  <div>
    <h5>Output 2</h5>
    <video width="540" height="380" autoPlay loop muted playsInline>
      <source src="http://localhost:5000/video/output_2.mp4" type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  </div>
</div>

</div>


      {/* Violation frames */}
      {VIOLATION_TYPES.map(type => (
        <div key={type} className="mb-5">
          <h3 className="text-capitalize">{type} Violations</h3>
          <div className="row">
            {frames[type] && frames[type].length > 0 ? (
              frames[type].map((frameUrl, index) => (
                <div className="col-md-4 mb-3" key={index}>
                  <img
                    src={`http://localhost:5000${frameUrl}`}
                    alt={`${type} violation frame ${index}`}
                    className="img-fluid rounded shadow"
                  />
                </div>
              ))
            ) : (
              <p>No {type} violation found for any vehilce tracked.</p>
            )}
          </div>
        </div>
      ))}
    </div>
  </>
  );

};

export default ViewViolatedFrame;
