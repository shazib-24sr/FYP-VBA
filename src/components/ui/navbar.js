import uetlogo from "../../assets/uet.png"
import rcetlogo from "../../assets/rcet.jfif"
import 'bootstrap/dist/css/bootstrap.min.css';

const Navbar = ({ onSwitch, onSubmit }) => (
    <>
    
    <nav className="navbar bg-body-tertiary bg-primary ">
  <div className="container-fluid ">
  <img src={uetlogo} alt="Logo" className="d-inline-block align-text-top" width="100" height="100"/>
       <h3>Vehicle Behavior Analysis for Multipoint Tracing and Violation Detection</h3>
      <img src={rcetlogo} alt="Logo" className="d-inline-block align-text-top"  width="100" height="100"/>
    
  </div>
</nav>

</>
);
export default Navbar;