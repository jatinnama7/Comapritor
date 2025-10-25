import User from '../models/User.js';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { sendOtpEmail, sendOtpSms } from '../utils/sendOtp.js';

function generateOtp() {
  return Math.floor(1000 + Math.random() * 9000).toString();
}

export const register = async (req, res) => {
  const { name, email, phone, password } = req.body;
  const hashed = await bcrypt.hash(password, 10);
  const otp = generateOtp();
  const expires = Date.now() + 5 * 60 * 1000;

  try {
    const user = new User({ name, email, phone, password: hashed, otp, otpExpires: expires });
    await user.save();
    await sendOtpEmail(email, otp);
    await sendOtpSms(phone, otp);
    res.status(201).json({ message: 'OTP sent to email and phone' });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

export const verifyOtp = async (req, res) => {
  const { email, otp } = req.body;
  const user = await User.findOne({ email });

  if (!user || user.otp !== otp || Date.now() > user.otpExpires) {
    return res.status(400).json({ error: 'Invalid or expired OTP' });
  }

  user.isVerified = true;
  user.otp = null;
  await user.save();
  res.json({ message: 'OTP verified successfully' });
};

export const login = async (req, res) => {
  const { email, password, otp } = req.body;
  const user = await User.findOne({ email });

  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(400).json({ error: 'Invalid credentials' });
  }

  if (!user.isVerified) {
    return res.status(403).json({ error: 'Please verify your OTP' });
  }

  const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1d' });
  res.json({ token, user: { name: user.name, email: user.email } });
};

export const forgotPassword = async (req, res) => {
  const { email } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(404).json({ error: 'Email not found' });

  const otp = generateOtp();
  user.otp = otp;
  user.otpExpires = Date.now() + 5 * 60 * 1000;
  await user.save();
  await sendOtpEmail(email, otp);
  res.json({ message: 'OTP sent to email for password reset' });
};

export const resetPassword = async (req, res) => {
  const { email, otp, newPassword } = req.body;
  const user = await User.findOne({ email });

  if (!user || user.otp !== otp || Date.now() > user.otpExpires) {
    return res.status(400).json({ error: 'Invalid or expired OTP' });
  }

  user.password = await bcrypt.hash(newPassword, 10);
  user.otp = null;
  await user.save();
  res.json({ message: 'Password reset successfully' });
};
