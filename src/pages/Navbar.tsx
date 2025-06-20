import { FaGlobe } from 'react-icons/fa';
import "tailwindcss";
import Button from './Button'; // Import the Button component
import './Navbar.css';


const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        {/* Replace the logo image with SparklesText */}
        <div className="logo">
          Comparitor
        </div>
        <a href="#" className="nav-link">Best Practices</a>
        <a href="#" className="nav-link">Help Center</a>
        <a href="#" className="nav-link">Pricing</a>
      </div> 

      <div className="navbar-right">
        <div className="language-selector">
          <FaGlobe size={16} />
          <span>English</span>
          <svg
            className="dropdown-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>

        {/* Here we are rendering the Button component */}
        <Button />
      </div>
    </nav>
  );
};

export default Navbar;
