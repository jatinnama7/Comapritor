// import { FaGlobe } from 'react-icons/fa';
// import "tailwindcss";
// import Button from './Button'; // Import the Button component
// import './Navbar.css';
// import { SparklesText } from "../Components/sparkles-text"



// const Navbar = () => {
//   return (
//     <nav className="navbar">
//         <div  style = {{transform:"scale(0.8)", transformOrigin: "left center" }} >
//          <SparklesText text= "Comparitor"/>
//         </div>
//       <div className="navbar-left">
//         {/* Replace the logo image with SparklesText */}
//         <a href="#" className="nav-link">Best Practices</a>
//         <a href="#" className="nav-link">Help Center</a>
//         <a href="#" className="nav-link">Pricing</a>
//          <a href="#" className="nav-link">Pricing</a>
//       </div> 

//       <div className="navbar-right">
//         <div className="language-selector">
//           <FaGlobe size={16} />
//           <span>English</span>
//           <svg
//             className="dropdown-icon"
//             fill="none"
//             stroke="currentColor"
//             viewBox="0 0 24 24"
//           >
//             <path
//               strokeLinecap="round"
//               strokeLinejoin="round"
//               strokeWidth={2}
//               d="M19 9l-7 7-7-7"
//             />
//           </svg>
//         </div>

//         {/* Here we are rendering the Button component */}
//         <Button />
//       </div>
//     </nav>
//   );
// };

// export default Navbar;
import { FaGlobe } from "react-icons/fa";
import "tailwindcss";
import Button from "./Button";
import "./Navbar.css";
import { SparklesText } from "../Components/sparkles-text";
import { useState } from "react";
import introVideo from "../assets/intro.mp4"; // adjust path if needed
import { Home, User, Briefcase, FileText } from 'lucide-react'
import { NavBar } from "@/Components/ui/tubelight-navbar"

const Navbar = () => {
  const [showVideo, setShowVideo] = useState(false);

  const handlePlayIntro = () => {
    setShowVideo(true);
  };

  return (
    <>
      <nav className="navbar">
        {/* Logo section with click to play video */}
        <div
          className="logo"
          style={{ transform: "scale(0.8)", transformOrigin: "left center", cursor: "pointer" }}
          onClick={handlePlayIntro}
        >
          <SparklesText text="Comparitor" />
        </div>

        <div className="navbar-left">
          <a href="#" className="nav-link">Best Practices</a>
          <a href="#" className="nav-link">Help Center</a>
          <a href="#" className="nav-link">Pricing</a>
        </div>

        <div className="navbar-right">
          <div className="language-selector">
            <FaGlobe size={16} />
            <span>English</span>
            <svg className="dropdown-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          <Button />
        </div>
      </nav>

      {/* Video Overlay */}
      {showVideo && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center">
          <video
            src={introVideo}
            autoPlay
            controls
            onEnded={() => setShowVideo(false)}
            className="w-screen h-screen object-cover"
          />
         
        </div>
      )}
    </>
  );
};

export default Navbar;
