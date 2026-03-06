import express from "express";
import { PORT } from "./config/env.js";


import messagesRoutes from "./routes/messages.route.js";



const app = express();

app.use(express.json());// req.body

app.get("/", (req, res) => {res.send("Welcome")});
app.use("/messages", messagesRoutes);

app.listen(PORT, async () => {
    console.log(`Server running on port http://localhost:${PORT}`);
});
