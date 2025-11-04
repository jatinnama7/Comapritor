import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  phone: String,
  password: String,
  otp: String,
  otpExpires: Date,
   sessionId: { type: String, default: null },
});

const User = mongoose.model("User", userSchema);
export default User;
