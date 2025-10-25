import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Component } from "@/Components/hyperspeed";

const Loading = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");

  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Play sound
    const audio = new Audio('/src/assets/warp-speed.mp3');
    audio.volume = 1;
    audio.play().catch((e) => {
      console.warn("Autoplay failed:", e);
    });

    // Start timer
    const timer = setTimeout(() => {
      setFadeOut(true);
      setTimeout(() => {
        navigate(`/product?query=${encodeURIComponent(query || "")}`);
        // navigate(`/search?query=${encodeURIComponent(query || "")}`);
      }, 800); // match fade-out duration
    }, 15568);

    return () => {
      clearTimeout(timer);
      audio.pause();
      audio.currentTime = 0;
    };
  }, [navigate, query]);

  return (
    <>
      <style>
        {`
          .fade-container {
            width: 100%;
            height: 100vh;
            background-color: black;
            animation: fadeIn 0.8s ease-in-out forwards;
          }

          .fade-container.fade-out {
            animation: fadeOut 0.8s ease-in-out forwards;
          }

          @keyframes fadeIn {
            from { opacity: 0; }
            to   { opacity: 1; }
          }

          @keyframes fadeOut {
            from { opacity: 1; }
            to   { opacity: 0; }
          }
        `}
      </style>

      <div className={`fade-container ${fadeOut ? 'fade-out' : ''}`}>
        <Component
          effectOptions={{
            onSpeedUp: () => console.log("Speeding up!"),
            onSlowDown: () => console.log("Slowing down!"),
            distortion: 'turbulentDistortion',
            length: 400,
            roadWidth: 10,
            islandWidth: 2,
            lanesPerRoad: 4,
            fov: 90,
            fovSpeedUp: 150,
            speedUp: 2,
            carLightsFade: 0.4,
            totalSideLightSticks: 20,
            lightPairsPerRoadWay: 40,
            shoulderLinesWidthPercentage: 0.05,
            brokenLinesWidthPercentage: 0.1,
            brokenLinesLengthPercentage: 0.5,
            lightStickWidth: [0.12, 0.5],
            lightStickHeight: [1.3, 1.7],
            movingAwaySpeed: [60, 80],
            movingCloserSpeed: [-120, -160],
            carLightsLength: [400 * 0.03, 400 * 0.2],
            carLightsRadius: [0.05, 0.14],
            carWidthPercentage: [0.3, 0.5],
            carShiftX: [-0.8, 0.8],
            carFloorSeparation: [0, 5],
            colors: {
              roadColor: 0x080808,
              islandColor: 0x0a0a0a,
              background: 0x000000,
              shoulderLines: 0xFFFFFF,
              brokenLines: 0xFFFFFF,
              leftCars: [0xD856BF, 0x6750A2, 0xC247AC],
              rightCars: [0x03B3C3, 0x0E5EA5, 0x324555],
              sticks: 0x03B3C3,
            }
          }}
        />
      </div>
    </>
  );
};

export default Loading;
