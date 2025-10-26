"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";
import { AnimatedBeam } from "../Components/animated-beam";
import FuturisticProductCard from "@/Components/FuturisticProductCard";

const Product: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const cardRefs = [
    useRef<HTMLDivElement>(null),
    useRef<HTMLDivElement>(null),
    useRef<HTMLDivElement>(null),
  ];

  const [fadeIn, setFadeIn] = useState(false);
  const [beamReady, setBeamReady] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [selectedCardIndexes, setSelectedCardIndexes] = useState<number[]>([]);
  const [completedBeams, setCompletedBeams] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<"product" | "productlist">(
    "product"
  );
  const [direction, setDirection] = useState<1 | -1>(1);

  useEffect(() => {
    setFadeIn(true);
  }, []);

  useEffect(() => {
    if (
      selectedCardIndexes.length > 0 &&
      completedBeams === selectedCardIndexes.length
    ) {
      setBeamReady(true);
    }
  }, [completedBeams, selectedCardIndexes]);

  // Restore beamReady if returning to product page
  useEffect(() => {
    if (currentPage === "product" && selectedCardIndexes.length > 0) {
      setBeamReady(true);
    }
  }, [currentPage]);

  const handleCompare = async () => {
    if (!beamReady || selectedCardIndexes.length === 0) return;
    setIsTransitioning(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    window.location.href = "/compared";
  };

  const handleSelect = (index: number, selected: boolean) => {
    setBeamReady(false);
    setCompletedBeams(0);
    setSelectedCardIndexes((prev) =>
      selected ? [...prev, index] : prev.filter((i) => i !== index)
    );
  };

  const handleSwipe = (e: any, { offset, velocity }: any) => {
    const swipe = offset.x * velocity.x;
    if (swipe < -1000 && currentPage === "product") {
      setDirection(1);
      setCurrentPage("productlist");
    } else if (swipe > 1000 && currentPage === "productlist") {
      setDirection(-1);
      setCurrentPage("product");
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" && currentPage === "product") {
        setDirection(1);
        setCurrentPage("productlist");
      } else if (e.key === "ArrowLeft" && currentPage === "productlist") {
        setDirection(-1);
        setCurrentPage("product");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentPage]);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        backgroundColor: "#000",
      }}
    >
      <motion.div
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={handleSwipe}
        style={{ width: "100%", height: "100%" }}
      >
        <AnimatePresence custom={direction} mode="wait">
          {currentPage === "product" ? (
            <motion.div
              key="product"
              custom={direction}
              initial={{ x: direction === 1 ? 300 : -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: direction === 1 ? 300 : -300, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              style={{
                backgroundColor: "#000000",
                height: "100vh",
                width: "100vw",
                padding: "2rem",
                opacity: fadeIn ? 1 : 0,
                position: "relative",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {/* Cards */}
              <div className="flex gap-10" style={{ marginBottom: "4rem" }}>
                {[0, 1, 2].map((index) => (
                  <div 
                  key={index} 
                  ref={cardRefs[index]}
                  >
                    <FuturisticProductCard
                      isSelected={selectedCardIndexes.includes(index)}
                      onSelect={(selected) => handleSelect(index, selected)}
                    />
                  </div>
                ))}
              </div>

              {/* Compare Button */}
              <div className="absolute bottom-10 left-1/2 -translate-x-1/2">
                <button
                  ref={buttonRef}
                  onClick={handleCompare}
                  disabled={!beamReady || selectedCardIndexes.length === 0}
                  className={`relative group px-4 py-2 rounded-lg font-semibold text-sm border-2 
                    text-white transition-all duration-300 ease-out focus:outline-none focus:ring-4 focus:ring-cyan-500/30 
                    ${
                      beamReady && selectedCardIndexes.length > 0
                        ? "cursor-pointer"
                        : "cursor-not-allowed opacity-50"
                    }`}
                  style={{
                    background:
                      "linear-gradient(135deg, rgba(6, 182, 212, 0.8), rgba(147, 51, 234, 0.8))",
                  }}
                >
                  <motion.div
                    className="absolute inset-0 rounded-lg blur-xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20"
                    animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.8, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <span className="relative z-10 flex items-center gap-2">
                    <motion.div
                      animate={
                        beamReady
                          ? { rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] }
                          : {}
                      }
                      transition={{ duration: 0.5 }}
                    >
                      <Sparkles className="w-4 h-4" />
                    </motion.div>
                    Compare with AI
                    <motion.div
                      animate={beamReady ? { x: [0, 5, 0] } : {}}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      <ArrowRight className="w-4 h-4" />
                    </motion.div>
                  </span>
                </button>
              </div>

              {/* Beams (visible only on product page) */}
              <AnimatePresence>
                {currentPage === "product" &&
                  selectedCardIndexes.map((i, idx) => {
                    const reverseMap: { [key: number]: boolean } = {
                      0: false,
                      1: false,
                      2: true,
                    };
                    return (
                      <AnimatedBeam
                        key={`beam-${i}`}
                        containerRef={containerRef}
                        fromRef={cardRefs[i]}
                        toRef={buttonRef}
                        curvature={200}
                        pathColor="#ccc"
                        pathOpacity={0.3}
                        gradientStartColor="#06b6d4"
                        gradientStopColor="#9333ea"
                        duration={2 + idx * 0.1}
                        pathWidth={4}
                        reverse={reverseMap[i] || false}
                        delay={idx * 0.3}
                        onAnimationComplete={() =>
                          setCompletedBeams((prev) => prev + 1)
                        }
                      />
                    );
                  })}
              </AnimatePresence>

              {/* Transition screen */}
              <AnimatePresence>
                {isTransitioning && (
                  <motion.div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1 }}
                  >
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="text-center text-white"
                    >
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                        className="text-cyan-400 text-6xl mb-4"
                      >
                        ⚡
                      </motion.div>
                      <h2 className="text-2xl font-bold mb-4">
                        Initializing AI Comparison...
                      </h2>
                      <div className="text-lg">Please wait</div>
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ) : (
            // <motion.div
            //   key="productlist"
            //   custom={direction}
            //   initial={{ x: direction === 1 ? 300 : -300, opacity: 0 }}
            //   animate={{ x: 0, opacity: 1 }}
            //   exit={{ x: direction === 1 ? 300 : -300, opacity: 0 }}
            //   transition={{ duration: 0.3, ease: "easeInOut" }}
            //   style={{
            //     width: "100vw",
            //     height: "100vh",
            //     backgroundColor: "#000",
            //     color: "#fff",
            //     display: "flex",
            //     alignItems: "center",
            //     justifyContent: "center",
            //     fontSize: "24px",
            //   }}
            // >
            //   This is an empty React page.
            // </motion.div>
          
           <motion.div
  key="productlist"
  custom={direction}
  initial={{ x: direction === 1 ? 300 : -300, opacity: 0 }}
  animate={{ x: 0, opacity: 1 }}
  exit={{ x: direction === 1 ? 300 : -300, opacity: 0 }}
  transition={{ duration: 0.3, ease: "easeInOut" }}
  style={{
    width: "100vw",
    height: "100vh",
    backgroundColor: "#000",
    color: "#fff",
    padding: "2rem",
    overflowY: "auto",
    scrollbarWidth: "none", // for Firefox
    msOverflowStyle: "none", // for IE/Edge
  }}
>
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: "1rem",
      
    }}
  >
    {Array.from({ length: 32 }).map((_, index) => (
      <div
        key={index}
        style={{
          transform: "scale(0.9)", // make it 80% of original size
          transformOrigin: "top ",
          
        }}
      >
        <FuturisticProductCard isSelected={false} onSelect={() => {}} />
      </div>
    ))}
  </div>
</motion.div>



          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default Product;
