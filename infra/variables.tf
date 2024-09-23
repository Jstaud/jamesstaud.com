# variables.tf
variable "digitalocean_token" {
  description = "DigitalOcean API token"
  type        = string
}

variable "github_token" {
  description = "GitHub token for accessing the repository"
  type        = string
  default     = "" # Optional: You can set a default value or leave it empty
}

# variable "mongodb_public_key" {
#   description = "MongoDB Atlas public API key"
#   type        = string
# }

# variable "mongodb_private_key" {
#   description = "MongoDB Atlas private API key"
#   type        = string
# }

# variable "mongodb_project_id" {
#   description = "MongoDB Atlas project ID"
#   type        = string
# }

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
}

variable "cloudflare_email" {
  description = "Cloudflare account email"
  type        = string
}

variable "cloudflare_api_key" {
  description = "Cloudflare API key"
  type        = string
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID"
  type        = string
}
