import express from "express";
import { PORT } from "./config/env.js";

import authRoutes from "./routes/auth.route.js";
import messagesRoutes from "./routes/messages.route.js";
import { connectDb } from "./database/mongoAtlas.js";


const app = express();

app.use(express.json());// req.body

app.use("/auth", authRoutes);
app.use("/messages", messagesRoutes);

app.listen(PORT, async () => {
    console.log(`Server running on port http://localhost:${PORT}`);
    await connectDb();
});
