"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/Utils";

interface ScreenBorderLightProps {
  lightColor?: string;
  duration?: number;
  glowIntensity?: number;
  trigger?: boolean;
}

const ScreenBorderLight: React.FC<ScreenBorderLightProps> = ({
  lightColor = "#00d9ff",
  duration = 1.8,
  glowIntensity = 20,
  trigger = false,
}) => {
  if (!trigger) return null;

  return (
    <>
      {/* Left Beam */}
      <motion.div
        className="absolute w-1 h-1 rounded-full"
        style={{
          backgroundColor: lightColor,
          boxShadow: `0 0 ${glowIntensity}px ${lightColor}, 0 0 ${
            glowIntensity * 2
          }px ${lightColor}`,
          zIndex: 40,
          left: 0,
          top: "50%",
        }}
        initial={{ x: 0, y: 0 }}
        animate={{
          x: [0, 0, "100vw", "100vw", "100vw"],
          y: [0, "-50vh", "-50vh", "50vh", "50vh"],
        }}
        transition={{
          duration,
          ease: [0.4, 0, 0.2, 1],
          times: [0, 0.25, 0.5, 0.75, 1],
        }}
      />

      {/* Right Beam */}
      <motion.div
        className="absolute w-1 h-1 rounded-full"
        style={{
          backgroundColor: lightColor,
          boxShadow: `0 0 ${glowIntensity}px ${lightColor}, 0 0 ${
            glowIntensity * 2
          }px ${lightColor}`,
          zIndex: 40,
          right: 0,
          top: "50%",
        }}
        initial={{ x: 0, y: 0 }}
        animate={{
          x: [0, 0, "-100vw", "-100vw", "-100vw"],
          y: [0, "50vh", "50vh", "-50vh", "-50vh"],
        }}
        transition={{
          duration,
          ease: [0.4, 0, 0.2, 1],
          times: [0, 0.25, 0.5, 0.75, 1],
        }}
      />

      {/* Border Glow */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        style={{
          border: `2px solid ${lightColor}`,
          boxShadow: `inset 0 0 ${glowIntensity}px ${lightColor}`,
          zIndex: 30,
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 0.2, 0.6, 1] }}
        transition={{ duration }}
      />
    </>
  );
};

export default ScreenBorderLight;
