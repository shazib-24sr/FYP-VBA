import React, { useState } from 'react';
import './SignIn.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Navbar from '../ui/navbar';
import { Link, useNavigate } from 'react-router-dom';

const SignUp = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async () => {
    try {
      const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Registration successful");
        navigate('/');
      } else {
        alert(data.error || "Registration failed");
      }
    } catch (error) {
      console.error('Error:', error);
      alert("Server error");
    }
  };

  return (
    <>
      <Navbar />
      <section className="vh-100">
        <div className="container-fluid h-custom">
          <div className="row d-flex justify-content-center align-items-center h-100">
            <div className="col-md-9 col-lg-6 col-xl-5">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-login-form/draw1.webp"
                   className="img-fluid" alt="Sample" />
            </div>
            <div className="col-md-8 col-lg-6 col-xl-4 offset-xl-1">
              <form>
                <div className="form-outline mb-4">
                  <input type="text" name="name" value={form.name}
                         onChange={handleChange}
                         className="form-control form-control-lg"
                         placeholder="Enter your full name" />
                  <label className="form-label">Full Name</label>
                </div>

                <div className="form-outline mb-4">
                  <input type="email" name="email" value={form.email}
                         onChange={handleChange}
                         className="form-control form-control-lg"
                         placeholder="Enter a valid email address" />
                  <label className="form-label">Email address</label>
                </div>

                <div className="form-outline mb-3">
                  <input type="password" name="password" value={form.password}
                         onChange={handleChange}
                         className="form-control form-control-lg"
                         placeholder="Enter password" />
                  <label className="form-label">Password</label>
                </div>

                <div className="text-center text-lg-start mt-4 pt-2">
                  <button type="button" className="btn btn-primary btn-lg"
                          onClick={handleRegister}
                          style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}>
                    Register
                  </button>
                  <p className="small fw-bold mt-2 pt-1 mb-0">
                    Already have an account? <Link to="/" className="link-danger">Login</Link>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
    </>
  );
};

export default SignUp;
