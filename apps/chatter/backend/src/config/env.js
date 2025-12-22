import { config } from "dotenv";

if (process.env.KUBERNETES_SERVICE_HOST === undefined) {
    config({ path: `.env.${process.env.NODE_ENV || 'development'}.vps` });
}
export const {
    PORT,
    MONGODB_URI,
} = process.env;