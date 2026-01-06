terraform {
  required_version = ">= 1.0.0"

  required_providers {
    # This allows us to run the remote SSH commands (remote-exec)
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2.0"
    }
    # This helps with local file manipulation (local-exec)
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4.0"
    }
  }
}

# We don't need a specific 'provider' block for null or local
# as they don't require extra configuration, but the
# 'terraform' block above tells it to download them.