variable "vps_ip" {
  description = "The public IP address of your Hostinger VPS"
  type        = string
}

variable "vps_password" {
  description = "The root password for your VPS (set during Hostinger OS reinstall)"
  type        = string
  sensitive   = true # This ensures the password isn't printed in your terminal logs
}