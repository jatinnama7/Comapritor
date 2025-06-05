"use client";

import { useRef } from "react";
import { AnimatedBeam } from "@/Components/animated-beam"; // Adjust if needed

export default function Search() {
  const containerRef = useRef<HTMLDivElement>(null);

  // Central node
  const centerRef = useRef<HTMLDivElement>(null);

  // Left nodes
  const googleDriveRef = useRef<HTMLDivElement>(null);
  const notionRef = useRef<HTMLDivElement>(null);
  const whatsappRef = useRef<HTMLDivElement>(null);

  // Right nodes
  const googleDocsRef = useRef<HTMLDivElement>(null);
  const zapierRef = useRef<HTMLDivElement>(null);
  const messengerRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={containerRef}
      style={{
        backgroundColor: "black",
        height: "100vh",
        width: "100vw",
        position: "relative",
      }}
    >
      {/* Center logo */}
      <div
        ref={centerRef}
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          backgroundColor: "white",
          borderRadius: "50%",
          padding: 16,
        }}
      >
        <img src="/src/assets/settings.svg" alt="OpenAI" width={40} height={40} />
      </div>

      {/* Left icons */}
      {[
        { ref: googleDriveRef, src: "/src/assets/amazon.svg", top: "25%", left: "15%"},
        { ref: notionRef, src: "/src/assets/myntra.svg", top: "45%", left: "15%" },
        { ref: whatsappRef, src: "/src/assets/flipkart.svg", top: "65%", left: "15%" },
      ].map(({ ref, src, top, left }, i) => (
        <div
          key={i}
          ref={ref}
          style={{
            position: "absolute",
            top,
            left,
            transform: "translate(-50%, -50%)",
            backgroundColor: "white",
            borderRadius: "50%",
            padding: 12,
          }}
        >
          <img src={src} alt="" width={32} height={32} />
        </div>
      ))}

      {/* Right icons */}
      {[
        { ref: googleDocsRef, src: "/src/assets/ebay.svg", top: "25%", right: "15%" },
        { ref: zapierRef, src: "/src/assets/Alibaba.png", top: "45%", right: "15%" },
        { ref: messengerRef, src: "/src/assets/JioMart.svg", top: "65%", right: "15%" },
      ].map(({ ref, src, top, right }, i) => (
        <div
          key={i}
          ref={ref}
          style={{
            position: "absolute",
            top,
            right,
            transform: "translate(50%, -50%)",
            backgroundColor: "white",
            borderRadius: "50%",
            padding: 12,
          }}
        >
          <img src={src} alt="" width={32} height={32} />
        </div>
      ))}

      {/* Beams */}
      <AnimatedBeam containerRef={containerRef} fromRef={googleDriveRef} toRef={centerRef} />
      <AnimatedBeam containerRef={containerRef} fromRef={notionRef} toRef={centerRef} />
      <AnimatedBeam containerRef={containerRef} fromRef={whatsappRef} toRef={centerRef} />

      <AnimatedBeam containerRef={containerRef} fromRef={googleDocsRef} toRef={centerRef}/>
      <AnimatedBeam containerRef={containerRef} fromRef={zapierRef} toRef={centerRef} />
      <AnimatedBeam containerRef={containerRef} fromRef={messengerRef} toRef={centerRef} />
    </div>
  );
}
