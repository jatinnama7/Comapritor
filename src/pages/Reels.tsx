import React from "react";
import ProductReelShowcase from "@/Components/ProductReelShowcase";
import "./Reels.css";

function Reels() {
  return (
    <div className="reels-page">
      <div className="reels-container">
        <ProductReelShowcase />
      </div>
    </div>
  );
}

export default Reels;
