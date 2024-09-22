# variables.tf
variable "digitalocean_token" {
  description = "DigitalOcean API token"
  type        = string
}

variable "mongodb_public_key" {
  description = "MongoDB Atlas public API key"
  type        = string
}

variable "mongodb_private_key" {
  description = "MongoDB Atlas private API key"
  type        = string
}

variable "mongodb_project_id" {
  description = "MongoDB Atlas project ID"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
}
