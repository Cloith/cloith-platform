import { config } from "dotenv";

if (process.env.KUBERNETES_SERVICE_HOST === undefined) {
    config({ path: `.env.${process.env.NODE_ENV || 'development'}.vps` });
}
export const {
    PORT,
    RESEND_API_KEY,
} = process.env;