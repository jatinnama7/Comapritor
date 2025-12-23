// import React from 'react'
// import './Explore.css'

// function Explorepage() {
//   return (
//     <div className="explore-container">
//         <p className="explore-subtext">Discover the best deals curated by our AI.</p>
        
//     </div>
//   )
// }

// export default Explorepage


import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Explorepage() {
  const [query, setQuery] = useState("");
  const [fadeOut, setFadeOut] = useState(false);
  const navigate = useNavigate();

  // 🔍 Backend Search Integration (same as Home)
  async function onKeyDown(e: { key: string; }) {
    if (e.key === "Enter" && query.trim()) {
      setFadeOut(true);

      try {
        const response = await fetch("http://127.0.0.1:8000/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: query.trim(),
            language: "en",
            country: "in",
          }),
        });

        if (!response.ok) throw new Error("Backend request failed");

        const data = await response.json();
        console.log("Products fetched:", data.cleaned_products);

        localStorage.setItem(
          "searchResults",
          JSON.stringify(data.cleaned_products || [])
        );

        setTimeout(() => {
          navigate(`/loading?query=${encodeURIComponent(query.trim())}`);
        }, 800);
      } catch (error) {
        console.error("Error fetching search:", error);
      }
    }
  }

  return (
    <div className={`explore-container ${fadeOut ? "fade-out" : "fade-in"}`}>


      {/* 🔍 SEARCH BLOCK (taken from Home page) */}
      <div className="floating-search-bar">
        <input
          type="text"
          placeholder="Search for a product..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <span className="search-icons"></span>
      </div>


    </div>
  );
}

export default Explorepage;

