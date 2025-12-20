import jwt from 'jsonwebtoken';

export const generateToken = (userId, res) => {
    const token = jwt.sign({userId}, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRES_IN,
    });

    res.cookie("jwt", token, {
        maxAge: Number(process.env.JWT_COOKIES_MAX_AGE),
        httpOnly: true, // prevents XSS attacks
        sameSite: "strict", // prevents CSRF attacks
        //add later after development
        //secure: process.env.NODE_ENV !== "development", // Only sends over HTTPS in production
    })
}