import React, { useState } from 'react';
import Spline from '@splinetool/react-spline';
import './Contacts.css';

function Contacts() {
  const [showMessage, setShowMessage] = useState(false);

  return (
    <div
      className="spline-wrapper"
      onMouseEnter={() => setShowMessage(true)}
      onMouseLeave={() => setShowMessage(false)}
    >
      <Spline className="static-spline"  scene="https://prod.spline.design/hTBnxFWE73d5rKcG/scene.splinecode" />


      {/* 🎨 Animated Speech Bubble */}
      {showMessage && (
        <div className="speech-bubble">
          Hi, I am Sarthak 👋
        </div>
      )}
    </div>
  );
}

export default Contacts;
