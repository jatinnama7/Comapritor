// import { useEffect, useRef, useState } from 'react';
// import * as THREE from 'three';

// // Declare the Hands type on the Window interface
// declare global {
//   interface Window {
//     Hands: any; // or specify a more precise type if known
//     Camera: any; // MediaPipe Camera utility
//   }
// }

// export default function ThreeD() {
//   const containerRef = useRef<HTMLDivElement>(null);
//   const videoRef = useRef(null);
//   const [loading, setLoading] = useState(true);
//   const [status, setStatus] = useState("Initializing AI...");

//   useEffect(() => {
//     // --- 1. THREE.JS SCENE SETUP ---
//     const scene = new THREE.Scene();
//     scene.background = new THREE.Color(0x0a0a0a);
    
//     const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
//     camera.position.z = 5;

//     const renderer = new THREE.WebGLRenderer({ antialias: true });
//     renderer.setSize(window.innerWidth, window.innerHeight);
//     renderer.setPixelRatio(window.devicePixelRatio);
//     if (containerRef.current) {
//       containerRef.current.appendChild(renderer.domElement);
//     }

//     // Lighting
//     const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
//     scene.add(ambientLight);
//     const pointLight = new THREE.PointLight(0x00ffff, 1);
//     pointLight.position.set(5, 5, 5);
//     scene.add(pointLight);

//     // Create 8 Product Placeholders
//     interface Product extends THREE.Mesh {
//       userData: {
//       id: number;
//       originalPos: THREE.Vector3;
//       };
//     }

//     const products: Product[] = [];
//     const colors = [0x00ffcc, 0xff00ff, 0xffff00, 0x0099ff, 0xff5500, 0x99ff00, 0xcc00ff, 0x00ffff];
    
//     for (let i = 0; i < 8; i++) {
//       const geometry = new THREE.BoxGeometry(1, 1, 1);
//       const material = new THREE.MeshStandardMaterial({ 
//         color: colors[i], 
//         roughness: 0.3, 
//         metalness: 0.8 
//       });
//       const cube = new THREE.Mesh(geometry, material) as unknown as Product;
      
//       // Arrange in a circle
//       const angle = (i / 8) * Math.PI * 2;
//       cube.position.set(Math.cos(angle) * 4, Math.sin(angle) * 2, -2);
//       cube.userData = { id: i, originalPos: cube.position.clone() };
      
//       scene.add(cube);
//       products.push(cube);
//     }

//     // --- 2. MEDIAPIPE HANDS SETUP ---
//     // Loading scripts dynamically for "self-contained" feel
//     const loadScripts = async () => {
//       const mpHands = document.createElement('script');
//       mpHands.src = "https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js";
//       const mpCamera = document.createElement('script');
//       mpCamera.src = "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";
      
//       document.head.appendChild(mpHands);
//       document.head.appendChild(mpCamera);

//       mpHands.onload = () => {
//         const hands = new window.Hands({
//           locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
//         });

//         hands.setOptions({
//           maxNumHands: 1,
//           modelComplexity: 1,
//           minDetectionConfidence: 0.5,
//           minTrackingConfidence: 0.5
//         });

//         let selectedProduct: Product | null = null;

//         hands.onResults((results: { multiHandLandmarks: string | any[]; }) => {
//           if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
//             const landmarks = results.multiHandLandmarks[0];
            
//             // Index and Thumb positions
//             const thumbTip = landmarks[4];
//             const indexTip = landmarks[8];
            
//             // Calculate Distance (Pinch)
//             const distance = Math.sqrt(
//               Math.pow(thumbTip.x - indexTip.x, 2) + 
//               Math.pow(thumbTip.y - indexTip.y, 2)
//             );

//             // Hand Position Mapping (Inverted X for mirror effect)
//             const handX = (0.5 - indexTip.x) * 10;
//             const handY = (0.5 - indexTip.y) * 10;

//             // GESTURE: PINCH (Select & Move)
//             if (distance < 0.05) {
//               if (!selectedProduct) {
//                 // Find nearest product
//                 selectedProduct = products.reduce((prev, curr) => {
//                   return (curr.position.distanceTo(new THREE.Vector3(handX, handY, 0)) < 
//                           prev.position.distanceTo(new THREE.Vector3(handX, handY, 0))) ? curr : prev;
//                 });
//                 setStatus("Product Grabbed!");
//               }
              
//               if (selectedProduct) {
//                 selectedProduct.position.lerp(new THREE.Vector3(handX, handY, 2), 0.1);
//                 selectedProduct.rotation.y += 0.05; // Auto-rotate while holding
//               }
//             } else {
//               // GESTURE: OPEN PALM (Deselect/Release)
//               if (selectedProduct) {
//                 selectedProduct.position.lerp(selectedProduct.userData.originalPos, 0.05);
//                 selectedProduct = null;
//                 setStatus("Hand Detected - Pinch to Grab");
//               }
//             }
//           }
//         });

//         const cameraFeed = new window.Camera(videoRef.current, {
//           onFrame: async () => {
//             await hands.send({ image: videoRef.current });
//           },
//           width: 640,
//           height: 480
//         });
//         cameraFeed.start();
//         setLoading(false);
//       };
//     };

//     loadScripts();

//     // --- 3. ANIMATION LOOP ---
//     const animate = () => {
//       requestAnimationFrame(animate);
      
//       // Subtle floating animation for all products
//       products.forEach((p, i) => {
//         p.position.y += Math.sin(Date.now() * 0.001 + i) * 0.002;
//         p.rotation.x += 0.005;
//       });

//       renderer.render(scene, camera);
//     };
//     animate();

//     // Cleanup
//     return () => {
//       renderer.dispose();
//       if (containerRef.current) containerRef.current.innerHTML = '';
//     };
//   }, []);

//   return (
//     <div style={{ width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden', background: '#000' }}>
//       {/* UI Overlay */}
//       <div style={{ 
//         position: 'absolute', top: 20, left: 20, zIndex: 10, 
//         color: 'white', fontFamily: 'sans-serif', pointerEvents: 'none' 
//       }}>
//         <h1 style={{ margin: 0, letterSpacing: '2px' }}>NEON SHOWROOM</h1>
//         <p style={{ color: '#00ffff' }}>{loading ? "System Loading..." : status}</p>
//         <div style={{ fontSize: '12px', opacity: 0.7 }}>
//           ✋ Open Palm: Hover | 🤏 Pinch: Grab & Rotate | ✊ Fist: Release
//         </div>
//       </div>

//       {/* Hidden Video Feed for AI Processing */}
//       <video 
//         ref={videoRef} 
//         style={{ 
//           position: 'absolute', bottom: 20, right: 20, 
//           width: 160, height: 120, borderRadius: '8px', 
//           border: '2px solid #00ffff', transform: 'scaleX(-1)' 
//         }} 
//       />

//       {/* Three.js Container */}
//       <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      
//       {loading && (
//         <div style={{
//           position: 'absolute', inset: 0, display: 'flex', 
//           alignItems: 'center', justifyContent: 'center', 
//           background: '#000', color: '#00ffff', zIndex: 20
//         }}>
//           INITIALIZING NEURAL ENGINE...
//         </div>
//       )}
//     </div>
//   );
// }


import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

declare global {
  interface Window {
    Hands: any;
    Camera: any;
  }
}

export default function ThreeD() {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Initializing AI...");

  useEffect(() => {
    // --- 1. THREE.JS SCENE SETUP ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);
    
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    if (containerRef.current) containerRef.current.appendChild(renderer.domElement);

    // Lighting (Enhanced for GLTF)
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const spotLight = new THREE.SpotLight(0x00ffff, 2);
    spotLight.position.set(5, 10, 5);
    scene.add(spotLight);

    // --- 2. VIRTUAL HANDS (VR STYLE) ---
    // Creating small spheres for joints to represent the hand in 3D
    const handJoints: THREE.Mesh[] = [];
    const jointMaterial = new THREE.MeshBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.6 });
    const jointGeo = new THREE.SphereGeometry(0.05, 8, 8);
    
    for (let i = 0; i < 21; i++) {
      const joint = new THREE.Mesh(jointGeo, jointMaterial);
      scene.add(joint);
      handJoints.push(joint);
    }

    // --- 3. PRODUCT LOADING (GLTF) ---
    const products: any[] = [];
    const loader = new GLTFLoader();

    // Load your shirt model
    interface ProductData {
      originalPos: THREE.Vector3;
      originalScale: number;
    }

    interface GLTFResult {
      scene: THREE.Group;
    }

    loader.load('/models/Shirt.glb', (gltf: GLTFResult) => {
      const model = gltf.scene;
      model.scale.set(1.5, 1.5, 1.5);
      model.position.set(0, -1.3, 0);
      model.userData = { originalPos: new THREE.Vector3(0, 0, 0), originalScale: 1.5 } as ProductData;
      scene.add(model);
      products.push(model);
      setLoading(false);
    });

    // --- 4. GESTURE ENGINE ---
    const loadScripts = async () => {
      const mpHands = document.createElement('script');
      mpHands.src = "https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js";
      const mpCamera = document.createElement('script');
      mpCamera.src = "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";
      document.head.appendChild(mpHands);
      document.head.appendChild(mpCamera);

      mpHands.onload = () => {
        const hands = new window.Hands({
          locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
        });

        hands.setOptions({
          maxNumHands: 2, // Enable two hands for zoom
          modelComplexity: 1,
          minDetectionConfidence: 0.7,
          minTrackingConfidence: 0.7
        });

        let selectedProduct: any = null;
        let initialDistance: number | null = null;

        hands.onResults((results: any) => {
          if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            const hand1 = results.multiHandLandmarks[0];
            
            // Update Virtual Hand Visualization
            hand1.forEach((pt: any, i: number) => {
              handJoints[i].position.set((0.5 - pt.x) * 10, (0.5 - pt.y) * 10, (1 - pt.z) * 2);
            });

            const thumb = hand1[4];
            const index = hand1[8];
            const pinchDist = Math.sqrt(Math.pow(thumb.x - index.x, 2) + Math.pow(thumb.y - index.y, 2));

            // 1. PINCH TO GRAB & ROTATE
            if (pinchDist < 0.05) {
              if (!selectedProduct && products.length > 0) selectedProduct = products[0];
              if (selectedProduct) {
                const targetX = (0.5 - index.x) * 8;
                const targetY = (0.5 - index.y) * 8;
                selectedProduct.position.lerp(new THREE.Vector3(targetX, targetY, 1), 0.1);
                selectedProduct.rotation.y += 0.05;
                setStatus("Inspecting Product...");
              }
            } else {
              if (selectedProduct && results.multiHandLandmarks.length < 2) {
                selectedProduct.position.lerp(selectedProduct.userData.originalPos, 0.05);
                selectedProduct = null;
              }
            }

            // 2. TWO-HAND ZOOM (Scaling)
            if (results.multiHandLandmarks.length === 2) {
              const hand2 = results.multiHandLandmarks[1];
              const currentDist = Math.sqrt(
                Math.pow(hand1[0].x - hand2[0].x, 2) + 
                Math.pow(hand1[0].y - hand2[0].y, 2)
              );

              if (initialDistance === null) initialDistance = currentDist;
              
              if (selectedProduct) {
                const scaleFactor = (currentDist / initialDistance);
                const newScale = Math.max(0.5, Math.min(4, selectedProduct.userData.originalScale * scaleFactor));
                selectedProduct.scale.set(newScale, newScale, newScale);
                setStatus("Zooming Product");
              }
            } else {
              initialDistance = null;
            }
          }
        });

        const cameraFeed = new window.Camera(videoRef.current, {
          onFrame: async () => { await hands.send({ image: videoRef.current }); },
          width: 640, height: 480
        });
        cameraFeed.start();
      };
    };

    loadScripts();

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      renderer.dispose();
      if (containerRef.current) containerRef.current.innerHTML = '';
    };
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden', background: '#000' }}>
      <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10, color: 'white', fontFamily: 'Orbitron, sans-serif' }}>
        <p>{status}</p>
        <div style={{ fontSize: '11px', background: 'rgba(0,255,255,0.1)', padding: '10px', borderRadius: '5px' }}>
          • 🤏 1 Hand Pinch: Drag & Rotate<br/>
          • 👐 2 Hands: Stretch to Zoom In/Out<br/>
          • 🖐️ Open Hand: Reset Position
        </div>
      </div>
      <video ref={videoRef} style={{ position: 'absolute', bottom: 20, right: 20, width: 200, height: 150, borderRadius: '10px', transform: 'scaleX(-1)', opacity: 0.6, border: '1px solid #00ffff' }} />
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}