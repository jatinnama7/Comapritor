import React, { useState } from "react";
import './login.css';

export default function LoginPage() {
  const [isActive, setIsActive] = useState(false);
  const [email, setEmail] = useState("");
  const [showSendOtp, setShowSendOtp] = useState(false);
  const [otpSent, setOtpSent] = useState(false);

  const handlePasswordFocus = () => {
    if (email.trim()) {
      setShowSendOtp(true);
    }
  };

  const handleSendOtp = () => {
    if (email.trim()) {
      // Simulate sending OTP
      setOtpSent(true);
      setTimeout(() => {
        setOtpSent(false); // Hide after a few seconds
      }, 3000);
    }
  };

  const renderOtpInputs = () => (
    <div className="otp-inputs">
      {[...Array(4)].map((_, index) => (
        <input
          key={index}
          type="text"
          inputMode="numeric"
          maxLength={1}
          className="otp-box"
          onInput={(e) => {
            const input = e.target as HTMLInputElement;
            input.value = input.value.replace(/[^0-9]/g, '');
            const next = input.nextElementSibling as HTMLInputElement | null;
            if (input.value && next) next.focus();
          }}
        />
      ))}
    </div>
  );

  return (
    <div className="wrapper">
      <div className={`container${isActive ? " active" : ""}`} id="container">
        
        {/* Sign Up */}
        <div className="form-container sign-up">
          <form>
            <h1>Create Account</h1>
            {renderOtpInputs()}
            <span>or use your email for registration</span>
            <input type="text" placeholder="Name" />
            <input type="email" placeholder="Email" />
            <input type="password" placeholder="Password" />
            <button type="button">Sign Up</button>
          </form>
        </div>

        {/* Sign In */}
        <div className="form-container sign-in">
          <form>
            <h1>Sign In</h1>
            {renderOtpInputs()}
            <span>or use your email and password</span>

            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <div className="password-with-button">
              <input
                type="password"
                placeholder="Password"
                onFocus={handlePasswordFocus}
              />
              {showSendOtp && (
                <button
                  type="button"
                  className="send-otp-btn"
                  onClick={handleSendOtp}
                >
                  Send OTP
                </button>
              )}
            </div>

            {otpSent && <p className="otp-message">OTP sent to your email</p>}

            <a href="#">Forgot Your Password?</a>
            <button type="button">Sign In</button>
          </form>
        </div>

        {/* Toggle Panel */}
        <div className="toggle-container">
          <div className="toggle">
            <div className="toggle-panel toggle-left">
              <h1>Welcome Back!</h1>
              <p>Enter your personal details to use all of the site's features</p>
              <button className="hidden" onClick={() => setIsActive(false)}>Sign In</button>
            </div>
            <div className="toggle-panel toggle-right">
              <h1>Hello, Friend!</h1>
              <p>Register with your personal details to use all of the site's features</p>
              <button className="hidden" onClick={() => setIsActive(true)}>Sign Up</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
