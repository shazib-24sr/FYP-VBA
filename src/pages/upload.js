import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/ui/navbar';
import SidebarLayout from '../components/ui/sidebar';
import 'bootstrap/dist/css/bootstrap.min.css';

const UploadPage = () => {
  const navigate = useNavigate();

  const [numVideos, setNumVideos] = useState(1);
  const [uploads, setUploads] = useState([null]);
  const [loading, setLoading] = useState(false);

  const handleVideoCountChange = (e) => {
    const count = parseInt(e.target.value);
    setNumVideos(count);
    const newUploads = Array(count).fill(null);
    setUploads(newUploads);
  };

  const handleFileChange = (index, file) => {
    const newUploads = [...uploads];
    newUploads[index] = file;
    setUploads(newUploads);
   
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();

    uploads.forEach((file, index) => {
      if (file) {
        formData.append(`video${index}`, file);
      }
    });

    

    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        alert('Upload successful!');
        navigate('/dashboard', { state: result });
      } else {
        alert('Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Error during upload:', error);
      alert('An error occurred while uploading.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <SidebarLayout>
        <div className="container py-5">
          <h2 className="text-center mb-4">Upload Surveillance Videos</h2>

          <form onSubmit={handleSubmit} className="bg-light p-4 rounded shadow-sm">
            <div className="mb-3">
              <label htmlFor="numVideos" className="form-label">Number of Videos:</label>
              <select
                id="numVideos"
                className="form-select"
                value={numVideos}
                onChange={handleVideoCountChange}
              >
                {[1, 2, 3, 4, 5].map((num) => (
                  <option key={num} value={num}>{num}</option>
                ))}
              </select>
            </div>

            {uploads.map((_, index) => (
              <div className="mb-3" key={index}>
                <label className="form-label">Video {index + 1}:</label>
                <input
                  type="file"
                  accept="video/*"
                  className="form-control"
                  onChange={(e) => handleFileChange(index, e.target.files[0])}
                  required
                />
              </div>
            ))}

           

            <div className="text-center">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Uploading...' : 'Upload & Analyze'}
              </button>
            </div>
          </form>
        </div>
      </SidebarLayout>
    </>
  );
};

export default UploadPage;
