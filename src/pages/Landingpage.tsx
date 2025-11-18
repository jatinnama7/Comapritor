import React from "react";
import "./Landing.css";

const Landingpage = () => {
  return (
    <div className="landing-wrapper">

      {/* BACKGROUND FLOATING LAYER (behind hero) */}
      <div className="float-wrapper" aria-hidden>

        {/* LEFT CLUSTER (9 divs: 2 big + 7 small) */}
        <div className="big-card left-big-1 card-filled"></div>
        <div className="big-card left-big-2"></div>

        <div className="sq left-sq-1" ></div>
        <div className="sq left-sq-2"></div>
        <div className="sq left-sq-3"></div>
        <div className="sq left-sq-4"></div>
        <div className="sq left-sq-5"></div>
        <div className="sq left-sq-6"></div>
        <div className="sq left-sq-7"></div>

        {/* RIGHT CLUSTER (10 divs: 2 big + 8 small) */}
        <div className="big-card right-big-1"></div>
        <div className="big-card right-big-2"></div>

        <div className="sq right-sq-1"></div>
        <div className="sq right-sq-2"></div>
        <div className="sq right-sq-3"></div>
        <div className="sq right-sq-4"></div>
        <div className="sq right-sq-5"></div>
        <div className="sq right-sq-6"></div>
        <div className="sq right-sq-7"></div>
        <div className="sq right-sq-8"></div>

      </div>

      {/* FOREGROUND HERO (centered, above floats) */}
      <main className="hero-content" role="main" aria-label="Hero section">
        <div className="hero-pills">
          <span className="pill pill-green">Fresh updates weekly</span>
          <span className="pill pill-purple">Flows now available for everyone</span>
        </div>

        <h1 className="hero-title">
              Compare Smarter<br />Shop Better
        </h1>

        <p className="hero-subtitle">
          Compare products from Amazon, Flipkart, and Meesho in one click with our smart AI-powered tool.
        </p>

        <button className="hero-btn">Start Exploring</button>
      </main>
    </div>
  );
};

export default Landingpage;
