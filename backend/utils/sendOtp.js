import dotenv from 'dotenv';
import nodemailer from 'nodemailer';
import twilio from 'twilio';


dotenv.config();

// EMAIL OTP
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL,
    pass: process.env.EMAIL_PASS,
  },
});

export const sendEmailOtp = async (email, otp) => {
  try {
    await transporter.sendMail({
      from: process.env.EMAIL,
      to: email,
      subject: 'Your OTP Code',
      text: `Your OTP is: ${otp}`,
    });
    console.log("✅ Email sent");
  } catch (err) {
    console.error("❌ Email error:", err);
  }
};

// SMS OTP
export const sendSmsOtp = async (phone, otp) => {
  try {
    const client = twilio(
      process.env.TWILIO_SID,
      process.env.TWILIO_AUTH_TOKEN
    );
    await client.messages.create({
      body: `Your OTP is: ${otp}`,
      from: process.env.TWILIO_PHONE_NUMBER,
      to: phone,
    });
    console.log("✅ SMS sent");
  } catch (err) {
    console.error("❌ SMS error:", err);
  }
};
