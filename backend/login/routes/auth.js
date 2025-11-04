// import express from "express";
// import bcrypt from "bcryptjs";
// import jwt from "jsonwebtoken";
// import User from "../models/User.js";
// import { sendEmailOtp, sendSmsOtp } from "../utils/sendOtp.js";

// const router = express.Router();

// const generateOtp = () => Math.floor(1000 + Math.random() * 9000).toString();

// router.post("/register", async (req, res) => {
//   const { name, email, phone, password } = req.body;

//   const existing = await User.findOne({ email });
//   if (existing) return res.status(400).json({ message: "Email already in use" });

//   const hashed = await bcrypt.hash(password, 10);
//   const otp = generateOtp();

//   const user = await User.create({
//     name,
//     email,
//     phone,
//     password: hashed,
//     otp,
//     otpExpires: new Date(Date.now() + 10 * 60 * 1000),
//   });

//   await sendEmailOtp(email, otp);
//   await sendSmsOtp(phone, otp);

//   res.json({ message: "OTP sent to email and phone" });
// });

// router.post("/verify-otp", async (req, res) => {
//   const { email, otp } = req.body;
//   const user = await User.findOne({ email });

//   if (!user || user.otp !== otp || user.otpExpires < new Date()) {
//     return res.status(400).json({ message: "Invalid or expired OTP" });
//   }

//   user.otp = null;
//   user.otpExpires = null;
//   await user.save();

//   res.json({ message: "OTP verified" });
// });

// router.post("/login", async (req, res) => {
//   const { email, password } = req.body;
//   const user = await User.findOne({ email });

//   if (!user || !(await bcrypt.compare(password, user.password))) {
//     return res.status(400).json({ message: "Invalid credentials" });
//   }

//   const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "7d" });
//   res.json({ token });
// });

// router.post("/forgot-password", async (req, res) => {
//   const { email } = req.body;
//   const user = await User.findOne({ email });
//   if (!user) return res.status(404).json({ message: "User not found" });

//   const otp = generateOtp();
//   user.otp = otp;
//   user.otpExpires = new Date(Date.now() + 10 * 60 * 1000);
//   await user.save();

//   await sendEmailOtp(email, otp);
//   res.json({ message: "OTP sent" });
// });

// router.post("/reset-password", async (req, res) => {
//   const { email, otp, newPassword } = req.body;
//   const user = await User.findOne({ email });

//   if (!user || user.otp !== otp || user.otpExpires < new Date()) {
//     return res.status(400).json({ message: "Invalid or expired OTP" });
//   }

//   user.password = await bcrypt.hash(newPassword, 10);
//   user.otp = null;
//   user.otpExpires = null;
//   await user.save();

//   res.json({ message: "Password reset successful" });
// });

// export default router;


// backend/routes/auth.js
import express from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import User from "../models/User.js";
import { sendEmailOtp, sendSmsOtp } from "../utils/sendOtp.js";
import { v4 as uuidv4 } from "uuid";


const router = express.Router();
const verifiedOtps = new Map(); // In-memory store: email -> verified status

const generateOtp = () => Math.floor(1000 + Math.random() * 9000).toString();

// ✅ Send OTP
router.post("/send-otp", async (req, res) => {
  const { email, phone } = req.body;

  if (!email || !phone) {
    return res.status(400).json({ message: "Email and phone are required" });
  }

  const otp = generateOtp();
  const expires = Date.now() + 10 * 60 * 1000;

  verifiedOtps.set(email, { otp, expires, phone });

  try {
    await sendEmailOtp(email, otp);
    await sendSmsOtp(phone, otp);
    res.json({ message: "OTP sent to email and phone" });
  } catch (err) {
    res.status(500).json({ message: "Failed to send OTP", error: err.message });
  }
});

// ✅ Verify OTP
router.post("/verify-otp", async (req, res) => {
  const { email, otp } = req.body;
  const record = verifiedOtps.get(email);

  if (!record || record.otp !== otp || Date.now() > record.expires) {
    return res.status(400).json({ message: "Invalid or expired OTP" });
  }

  verifiedOtps.set(email, { ...record, verified: true });
  res.json({ message: "OTP verified" });
});

// ✅ Register (only after OTP verification)
router.post("/register", async (req, res) => {
  const { name, email, phone, password } = req.body;

  const existing = await User.findOne({ email });
  if (existing) return res.status(400).json({ message: "Email already in use" });

  const otpRecord = verifiedOtps.get(email);
  if (!otpRecord || !otpRecord.verified || otpRecord.phone !== phone) {
    return res.status(403).json({ message: "OTP not verified" });
  }

  const hashed = await bcrypt.hash(password, 10);
  const user = await User.create({
    name,
    email,
    phone,
    password: hashed,
  });

  verifiedOtps.delete(email); // Clean up

  res.json({ message: "Registration successful" });
});

// ✅ Login
router.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(400).json({ message: "Invalid credentials" });
  }

  const sessionId = uuidv4(); // 🆕 Unique session
  user.sessionId = sessionId;
  await user.save();

  const token = jwt.sign(
    { id: user._id, sessionId }, // 🆕 Include session
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );

  res.json({ token });
});




// ✅ Forgot Password
router.post("/forgot-password", async (req, res) => {
  const { email } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(404).json({ message: "User not found" });

  const otp = generateOtp();
  const expires = Date.now() + 10 * 60 * 1000;
  verifiedOtps.set(email, { otp, expires });

  await sendEmailOtp(email, otp);
  res.json({ message: "OTP sent" });
});

// ✅ Reset Password
router.post("/reset-password", async (req, res) => {
  const { email, otp, newPassword } = req.body;
  const user = await User.findOne({ email });
  const record = verifiedOtps.get(email);

  if (!user || !record || record.otp !== otp || Date.now() > record.expires) {
    return res.status(400).json({ message: "Invalid or expired OTP" });
  }

  user.password = await bcrypt.hash(newPassword, 10);
  await user.save();
  verifiedOtps.delete(email);

  res.json({ message: "Password reset successful" });
});

export default router;
