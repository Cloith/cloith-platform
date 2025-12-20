import mongoose from 'mongoose';

export const connectDb = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGODB_URI);
        console.log('Connected to MONGODB', conn.connection.host);
    } catch (error) {
        console.error("Error connecting to MONGODB", error);
        process.exit(1); // 1 status code means fail, 0 means success
    }
};