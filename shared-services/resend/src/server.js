import express from "express";
import { PORT } from "./config/env.js";

const app = express();

app.use(express.json());

app.get("/", (req, res) => {res.send("Welcome to resend!")});


app.listen(PORT, async () => {
    console.log(`Server running on port http://localhost:${PORT}`);
});
