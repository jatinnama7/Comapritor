// import React, { useState } from "react";
// import './login.css';

// export default function LoginPage() {
//   const [isActive, setIsActive] = useState(false);
//   const [email, setEmail] = useState("");
//   const [showSendOtp, setShowSendOtp] = useState(false);
//   const [otpSent, setOtpSent] = useState(false);

//   const handlePasswordFocus = () => {
//     if (email.trim()) {
//       setShowSendOtp(true);
//     }
//   };

//   const handleSendOtp = () => {
//     if (email.trim()) {
//       setOtpSent(true);
//       setTimeout(() => {
//         setOtpSent(false);
//       }, 3000);
//     }
//   };

//   const renderOtpInputs = () => (
//     <div className="otp-inputs">
//       {[...Array(4)].map((_, index) => (
//         <input
//           key={index}
//           type="text"
//           inputMode="numeric"
//           maxLength={1}
//           className="otp-box"
//           onInput={(e) => {
//             const input = e.target as HTMLInputElement;
//             input.value = input.value.replace(/[^0-9]/g, '');
//             const next = input.nextElementSibling as HTMLInputElement | null;
//             if (input.value && next) next.focus();
//           }}
//         />
//       ))}
//     </div>
//   );

//   return (
//     <div className="wrapper">
//       <div className={`container${isActive ? " active" : ""}`} id="container">

//         {/* Sign Up */}
//         <div className="form-container sign-up">
//           <form>
//             <h1>Create Account</h1>
//             {renderOtpInputs()}
//             <span>or use your email for registration</span>

//             <input
//               type="text"
//               placeholder="Name"
//             />

//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />

//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//               />
//               {showSendOtp && (
//                 <button
//                   type="button"
//                   className="send-otp-btn"
//                   onClick={handleSendOtp}
//                 >
//                   Send OTP
//                 </button>
//               )}
//             </div>

//             {otpSent && <p className="otp-message">OTP sent to your email</p>}

//             <button type="button">Sign Up</button>
//           </form>
//         </div>

//         {/* Sign In */}
//         <div className="form-container sign-in">
//           <form>
//             <h1>Sign In</h1>
//             {renderOtpInputs()}
//             <span>or use your email and password</span>

//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />

//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//               />
//               {showSendOtp && (
//                 <button
//                   type="button"
//                   className="send-otp-btn"
//                   onClick={handleSendOtp}
//                 >
//                   Send OTP
//                 </button>
//               )}
//             </div>

//             {otpSent && <p className="otp-message">OTP sent to your email</p>}

//             <a href="#">Forgot Your Password?</a>
//             <button type="button">Sign In</button>
//           </form>
//         </div>

//         {/* Toggle Panel */}
//         <div className="toggle-container">
//           <div className="toggle">
//             <div className="toggle-panel toggle-left">
//               <h1>Welcome Back!</h1>
//               <p>Enter your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(false)}>Sign In</button>
//             </div>
//             <div className="toggle-panel toggle-right">
//               <h1>Hello, Friend!</h1>
//               <p>Register with your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(true)}>Sign Up</button>
//             </div>
//           </div>
//         </div>

//       </div>
//     </div>
//   );
// }
// import React, { useState } from "react";
// import './login.css';
// import { FaPhone } from "react-icons/fa";


// export default function LoginPage() {
//   const [isActive, setIsActive] = useState(false);
//   const [email, setEmail] = useState("");
//   const [phone, setPhone] = useState("");
//   const [showSendOtp, setShowSendOtp] = useState(false);
//   const [otpSent, setOtpSent] = useState(false);
//   const [otp, setOtp] = useState(["", "", "", ""]);

//   const handlePasswordFocus = () => {
//     if (email.trim()) {
//       setShowSendOtp(true);
//     }
//   };

//   const handleSendOtp = () => {
//     if (email.trim()) {
//       setOtpSent(true);
//       setTimeout(() => {
//         setOtpSent(false);
//       }, 3000);
//     }
//   };

//   const handleOtpChange = (value: string, index: number) => {
//     const newOtp = [...otp];
//     newOtp[index] = value;
//     setOtp(newOtp);
//   };

//   const renderOtpInputs = () => (
//     <div className="otp-inputs">
//       {otp.map((digit, index) => (
//         <input
//           key={index}
//           type="text"
//           inputMode="numeric"
//           maxLength={1}
//           className="otp-box"
//           autoComplete="off"
//           value={digit}
//           onChange={(e) => {
//             const val = e.target.value.replace(/[^0-9]/g, '');
//             handleOtpChange(val, index);
//             if (val && e.target.nextElementSibling instanceof HTMLInputElement) {
//               e.target.nextElementSibling.focus();
//             }
//           }}
//         />
//       ))}
//     </div>
//   );

//   return (
//     <div className="wrapper">
//       <div className={`container${isActive ? " active" : ""}`} id="container">

//         {/* Sign Up */}
//         <div className="form-container sign-up">
//           <form>
//             <h1>Create Account</h1>
//             {renderOtpInputs()}
//             <span>or use your email for registration</span>

//             <input
//               type="text"
//               placeholder="Name"
//               autoComplete="off"
//             />

//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />

//             <div className="phone-input">
//               <input
//                 type="tel"
//                 placeholder="Phone"
//                 value={phone}
//                 onChange={(e) => setPhone(e.target.value)}
//               />
//             </div>

//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//                 autoComplete="new-password"
//               />
//               {showSendOtp && (
//                 <button
//                   type="button"
//                   className="send-otp-btn"
//                   onClick={handleSendOtp}
//                 >
//                   Send OTP
//                 </button>
//               )}
//             </div>

//             {otpSent && <p className="otp-message">OTP sent to your email</p>}

//             <button type="button">Sign Up</button>
//           </form>
//         </div>

//         {/* Sign In */}
//         <div className="form-container sign-in">
//           <form>
//             <h1>Sign In</h1>
//             {renderOtpInputs()}
//             <span>or use your email and password</span>

//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />

//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//                 autoComplete="current-password"
//               />
//               {showSendOtp && (
//                 <button
//                   type="button"
//                   className="send-otp-btn"
//                   onClick={handleSendOtp}
//                 >
//                   Send OTP
//                 </button>
//               )}
//             </div>

//             {otpSent && <p className="otp-message">OTP sent to your email</p>}

//             <a href="#">Forgot Your Password?</a>
//             <button type="button">Sign In</button>
//           </form>
//         </div>

//         {/* Toggle Panel */}
//         <div className="toggle-container">
//           <div className="toggle">
//             <div className="toggle-panel toggle-left">
//               <h1>Welcome Back!</h1>
//               <p>Enter your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(false)}>Sign In</button>
//             </div>
//             <div className="toggle-panel toggle-right">
//               <h1>Hello, Friend!</h1>
//               <p>Register with your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(true)}>Sign Up</button>
//             </div>
//           </div>
//         </div>

//       </div>
//     </div>
//   );
// }
// import React, { useState } from "react";
// import './login.css';
// import { FaPhone } from "react-icons/fa";

// export default function LoginPage() {
//   const [isActive, setIsActive] = useState(false);
//   const [email, setEmail] = useState("");
//   const [phone, setPhone] = useState("");
//   const [name, setName] = useState("");
//   const [password, setPassword] = useState("");
//   const [newPassword, setNewPassword] = useState("");
//   const [showSendOtp, setShowSendOtp] = useState(false);
//   const [otpSent, setOtpSent] = useState(false);
//   const [otp, setOtp] = useState(["", "", "", ""]);

//   const getOtp = () => otp.join("");

//   const handlePasswordFocus = () => {
//     if (email.trim()) {
//       setShowSendOtp(true);
//     }
//   };

//   const handleOtpChange = (value: string, index: number) => {
//     const newOtp = [...otp];
//     newOtp[index] = value;
//     setOtp(newOtp);
//   };

//   const renderOtpInputs = () => (
//     <div className="otp-inputs">
//       {otp.map((digit, index) => (
//         <input
//           key={index}
//           type="text"
//           inputMode="numeric"
//           maxLength={1}
//           className="otp-box"
//           autoComplete="off"
//           value={digit}
//           onChange={(e) => {
//             const val = e.target.value.replace(/[^0-9]/g, '');
//             handleOtpChange(val, index);
//             if (val && e.target.nextElementSibling instanceof HTMLInputElement) {
//               e.target.nextElementSibling.focus();
//             }
//           }}
//         />
//       ))}
//     </div>
//   );

//   const handleRegister = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/register", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ name, email,  phone: "+91" + phone, password }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         alert("OTP sent to email and phone");
//       } else {
//         alert(data.error || "Registration failed");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleVerifyOtp = async () => {
//     setOtpSent(true);
//     setTimeout(() => setOtpSent(false), 3000);
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/verify-otp", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, otp: getOtp() }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         alert("OTP verified!");
//       } else {
//         alert(data.error || "OTP verification failed");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleLogin = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/login", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, password }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         alert("Login success");
//         localStorage.setItem("token", data.token);
//       } else {
//         alert(data.error || "Login failed");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleForgotPassword = async (e: React.MouseEvent) => {
//     e.preventDefault();
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/forgot-password", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         alert("OTP sent for password reset");
//       } else {
//         alert(data.error || "Error sending OTP");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   return (
//     <div className="wrapper">
//       <div className={`container${isActive ? " active" : ""}`} id="container">
//         {/* Sign Up */}
//         <div className="form-container sign-up">
//           <form>
//             <h1>Create Account</h1>
//             {renderOtpInputs()}
//             <span>or use your email for registration</span>
//             <input
//               type="text"
//               placeholder="Name"
//               autoComplete="off"
//               value={name}
//               onChange={(e) => setName(e.target.value)}
//             />
//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />
//             <div className="phone-input">
//               <input
//                 type="tel"
//                 placeholder="Phone"
//                 value={phone}
//                 onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))} // only digits
//                 maxLength={10}              
//               />
//             </div>
//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 autoComplete="new-password"
//               />
//               {showSendOtp && (
//                 <button type="button" className="send-otp-btn" onClick={handleVerifyOtp}>
//                   Send OTP
//                 </button>
//               )}
//             </div>
//             {otpSent && <p className="otp-message">OTP sent to your email</p>}
//             <button type="button" onClick={handleRegister}>Sign Up</button>
//           </form>
//         </div>

//         {/* Sign In */}
//         <div className="form-container sign-in">
//           <form>
//             <h1>Sign In</h1>
//             {renderOtpInputs()}
//             <span>or use your email and password</span>
//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />
//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 autoComplete="current-password"
//               />
//               {showSendOtp && (
//                 <button type="button" className="send-otp-btn" onClick={handleVerifyOtp}>
//                   Send OTP
//                 </button>
//               )}
//             </div>
//             {otpSent && <p className="otp-message">OTP sent to your email</p>}
//             <a href="#" onClick={handleForgotPassword}>Forgot Your Password?</a>
//             <button type="button" onClick={handleLogin}>Sign In</button>
//           </form>
//         </div>

//         {/* Toggle Panel */}
//         <div className="toggle-container">
//           <div className="toggle">
//             <div className="toggle-panel toggle-left">
//               <h1>Welcome Back!</h1>
//               <p>Enter your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(false)}>Sign In</button>
//             </div>
//             <div className="toggle-panel toggle-right">
//               <h1>Hello, Friend!</h1>
//               <p>Register with your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(true)}>Sign Up</button>
//             </div>
//           </div>
//         </div>

//       </div>
//     </div>
//   );
// }
// import React, { useState } from "react";
// import './login.css';
// import { FaPhone } from "react-icons/fa";
// import { useNavigate } from "react-router-dom";
// import { toast, ToastContainer } from 'react-toastify';
// import 'react-toastify/dist/ReactToastify.css';

// <ToastContainer 


//  position="top-right"
//   autoClose={3000}
//   hideProgressBar={false}
//   newestOnTop={true}
//   closeOnClick
//   pauseOnHover
//   draggable
//   theme="colored"/>

// export default function LoginPage() {
//   const navigate = useNavigate();
//   const [isActive, setIsActive] = useState(false);
//   const [email, setEmail] = useState("");
//   const [phone, setPhone] = useState("");
//   const [name, setName] = useState("");
//   const [password, setPassword] = useState("");
//   const [otp, setOtp] = useState(["", "", "", ""]);

//   const [showSendOtp, setShowSendOtp] = useState(false);
//   const [otpSent, setOtpSent] = useState(false);
//   const [otpRequested, setOtpRequested] = useState(false); // ✅ NEW

//   const getOtp = () => otp.join("");

//   const handlePasswordFocus = () => {
//     if (email.trim()) {
//       setShowSendOtp(true);
//     }
//   };

//   const handleOtpChange = (value: string, index: number) => {
//     const newOtp = [...otp];
//     newOtp[index] = value;
//     setOtp(newOtp);
//   };

//   const renderOtpInputs = () => (
//     <div className="otp-inputs">
//       {otp.map((digit, index) => (
//         <input
//           key={index}
//           type="text"
//           inputMode="numeric"
//           maxLength={1}
//           className="otp-box"
//           autoComplete="off"
//           value={digit}
//           onChange={(e) => {
//             const val = e.target.value.replace(/[^0-9]/g, '');
//             handleOtpChange(val, index);
//             if (val && e.target.nextElementSibling instanceof HTMLInputElement) {
//               e.target.nextElementSibling.focus();
//             }
//           }}
//         />
//       ))}
//     </div>
//   );

//   const handleSendOtp = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/send-otp", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, phone: "+91" + phone }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         setOtpRequested(true); // ✅ switch button to "Verify OTP"
//         setOtpSent(true);
//         toast.info("OTP sent to email and phone");
//       } else {
//         alert(data.message || "Failed to send OTP");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleVerifyOtp = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/verify-otp", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, otp: getOtp() }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         alert("OTP verified!");
//       } else {
//         alert(data.error || "OTP verification failed");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleRegister = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/register", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ name, email, phone: "+91" + phone, password }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         toast.success("Registration successfull");
//          navigate("/home"); 
//       } else {
//         alert(data.error || "Registration failed");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleLogin = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/login", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, password }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         toast.success("Login successfull");
//         localStorage.setItem("token", data.token);
//         navigate("/home");
//       } else {
//         alert(data.error || "Login failed");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   const handleForgotPassword = async (e: React.MouseEvent) => {
//     e.preventDefault();
//     try {
//       const res = await fetch("http://localhost:5000/api/auth/forgot-password", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email }),
//       });
//       const data = await res.json();
//       if (res.ok) {
//         alert("OTP sent for password reset");
//       } else {
//         alert(data.error || "Error sending OTP");
//       }
//     } catch (err) {
//       alert("Error: " + err);
//     }
//   };

//   return (
//     <div className="wrapper">
//       <div className={`container${isActive ? " active" : ""}`} id="container">

//         {/* Sign Up */}
//         <div className="form-container sign-up">
//           <form>
//             <h1>Create Account</h1>
//             {renderOtpInputs()}
//             <span>or use your email for registration</span>
//             <input
//               type="text"
//               placeholder="Name"
//               autoComplete="off"
//               value={name}
//               onChange={(e) => setName(e.target.value)}
//             />
//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />
//             <div className="phone-input">
//               <input
//                 type="tel"
//                 placeholder="Phone"
//                 value={phone}
//                 onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
//                 maxLength={10}
//               />
//             </div>
//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 autoComplete="new-password"
//               />
//               {showSendOtp && (
//                 otpRequested ? (
//                   <button type="button" className="send-otp-btn" onClick={handleVerifyOtp}>
//                     Verify OTP
//                   </button>
//                 ) : (
//                   <button type="button" className="send-otp-btn" onClick={handleSendOtp}>
//                     Send OTP
//                   </button>
//                 )
//               )}
//             </div>
//             {otpSent && <p className="otp-message">OTP sent to your email</p>}
//             <button type="button" onClick={handleRegister}>Sign Up</button>
//           </form>
//         </div>

//         {/* Sign In */}
//         <div className="form-container sign-in">
//           <form>
//             <h1>Sign In</h1>
//             {renderOtpInputs()}
//             <span>or use your email and password</span>
//             <input
//               type="email"
//               placeholder="Email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />
//             <div className="password-with-button">
//               <input
//                 type="password"
//                 placeholder="Password"
//                 onFocus={handlePasswordFocus}
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 autoComplete="current-password"
//               />
//               {showSendOtp && (
//                 otpRequested ? (
//                   <button type="button" className="send-otp-btn" onClick={handleVerifyOtp}>
//                     Verify OTP
//                   </button>
//                 ) : (
//                   <button type="button" className="send-otp-btn" onClick={handleSendOtp}>
//                     Send OTP
//                   </button>
//                 )
//               )}
//             </div>
//             {otpSent && <p className="otp-message">OTP sent to your email</p>}
//             <a href="#" onClick={handleForgotPassword}>Forgot Your Password?</a>
//             <button type="button" onClick={handleLogin}>Sign In</button>
//           </form>
//         </div>

//         {/* Toggle Panel */}
//         <div className="toggle-container">
//           <div className="toggle">
//             <div className="toggle-panel toggle-left">
//               <h1>Welcome Back!</h1>
//               <p>Enter your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(false)}>Sign In</button>
//             </div>
//             <div className="toggle-panel toggle-right">
//               <h1>Hello, Friend!</h1>
//               <p>Register with your personal details to use all of the site's features</p>
//               <button className="ghost" onClick={() => setIsActive(true)}>Sign Up</button>
//             </div>
//           </div>
//         </div>

//       </div>
//     </div>
//   );
// }
import React, { useState } from "react";
import './login.css';
import { useNavigate } from "react-router-dom";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const [isActive, setIsActive] = useState(false);
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState(["", "", "", ""]);
  const [showSendOtp, setShowSendOtp] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otpRequested, setOtpRequested] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);

  const getOtp = () => otp.join("");

  const handlePasswordFocus = () => {
    if (email.trim()) {
      setShowSendOtp(true);
    }
  };

  const handleOtpChange = (value: string, index: number) => {
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
  };

  const renderOtpInputs = () => (
    <div className="otp-inputs">
      {otp.map((digit, index) => (
        <input
          key={index}
          type="text"
          inputMode="numeric"
          maxLength={1}
          className="otp-box"
          autoComplete="off"
          value={digit}
          onChange={(e) => {
            const val = e.target.value.replace(/[^0-9]/g, '');
            handleOtpChange(val, index);
            if (val && e.target.nextElementSibling instanceof HTMLInputElement) {
              e.target.nextElementSibling.focus();
            }
          }}
        />
      ))}
    </div>
  );

  const handleSendOtp = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/auth/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, phone: "+91" + phone }),
      });
      const data = await res.json();
      if (res.ok) {
        setOtpRequested(true);
        setOtpSent(true);
        toast.info("OTP sent to email and phone");
      } else {
        toast.error(data.message || "Failed to send OTP");
      }
    } catch (err) {
      toast.error("Error: " + err);
    }
  };

  const handleVerifyOtp = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp: getOtp() }),
      });
      const data = await res.json();
      if (res.ok) {
        setOtpVerified(true);
        toast.success("OTP verified!");
      } else {
        toast.error(data.error || "OTP verification failed");
      }
    } catch (err) {
      toast.error("Error: " + err);
    }
  };

  const handleRegister = async () => {
    if (!name || !email || !phone || !password) {
      toast.warn("Please fill in all fields.");
      return;
    }
    if (!otpVerified) {
      toast.warn("Please verify your OTP first.");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, phone: "+91" + phone, password }),
      });
      const data = await res.json();
      if (res.ok) {
        toast.success("Registration successful");
         localStorage.setItem("isLoggedIn", "true");
          localStorage.setItem("isLoggedIn", "true");
        navigate("/");
      } else {
        toast.error(data.error || "Registration failed");
      }
    } catch (err) {
      toast.error("Error: " + err);
    }
  };

  const handleLogin = async () => {
    if (!email || !password) {
      toast.warn("Please fill in all fields.");
      return;
    }
    if (!otpVerified) {
      toast.warn("Please verify your OTP first.");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        toast.success("Login successful");
        localStorage.setItem("token", data.token);
         localStorage.setItem("isLoggedIn", "true");

        navigate("/");
      } else {
        toast.error(data.error || "Login failed");
      }
    } catch (err) {
      toast.error("Error: " + err);
    }
  };

  return (
    <div className="wrapper">
      <div className={`container${isActive ? " active" : ""}`} id="container">
        <div className="form-container sign-up">
          <form>
            <h1>Create Account</h1>
            {renderOtpInputs()}
            <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="tel" placeholder="Phone" value={phone} maxLength={10} onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))} />
            <div className="password-with-button">
              <input type="password" placeholder="Password" value={password} onFocus={handlePasswordFocus} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" />
              {showSendOtp && (
                otpRequested ? (
                  <button type="button" className="send-otp-btn" onClick={handleVerifyOtp}>Verify OTP</button>
                ) : (
                  <button type="button" className="send-otp-btn" onClick={handleSendOtp}>Send OTP</button>
                )
              )}
            </div>
          
            <button type="button" onClick={handleRegister}>Sign Up</button>
          </form>
        </div>

        <div className="form-container sign-in">
          <form>
            <h1>Sign In</h1>
            {renderOtpInputs()}
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <div className="password-with-button">
              <input type="password" placeholder="Password" value={password} onFocus={handlePasswordFocus} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
              {showSendOtp && (
                otpRequested ? (
                  <button type="button" className="send-otp-btn" onClick={handleVerifyOtp}>Verify OTP</button>
                ) : (
                  <button type="button" className="send-otp-btn" onClick={handleSendOtp}>Send OTP</button>
                )
              )}
            </div>
           
            <button type="button" onClick={handleLogin}>Sign In</button>
          </form>
        </div>

        <div className="toggle-container">
          <div className="toggle">
            <div className="toggle-panel toggle-left">
              <h1>Welcome Back!</h1>
              <p>Enter your personal details to use all of the site's features</p>
              <button className="ghost" onClick={() => setIsActive(false)}>Sign In</button>
            </div>
            <div className="toggle-panel toggle-right">
              <h1>Hello, Friend!</h1>
              <p>Register with your personal details to use all of the site's features</p>
              <button className="ghost" onClick={() => setIsActive(true)}>Sign Up</button>
            </div>
          </div>
        </div>
      </div>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        pauseOnHover
        draggable
        theme="colored"
      />
    </div>
  );
}
