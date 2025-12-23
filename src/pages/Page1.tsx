import React from 'react';
import './Page1.css';
import Navbar from './Navbar';
import ai from '../assets/ai.png';
// import { Cursor } from '@/Components/inverted-cursor';



const Page1 = () => {
  return (
    <>
      <Navbar />
      
      <div className="page1-container">
        <p className="intro-line">
          Hi, We're <span className="brand">Comparitor</span>
        </p>
        <p className="main-text">
          Your AI website team: Compare deals from Amazon, Flipkart, and Meesho in one smart place.
        </p>
        <p className="main-text">
Just search once, and our AI finds the best prices, reviews, and delivery options for you.        </p>
        <p className="get-started">Let's get started!</p>
        <img src={ai} alt="carte" className="cart-image" />
      </div>
      
    </>
    
  );
};

export default Page1;
