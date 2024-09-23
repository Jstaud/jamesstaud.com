# main.tf
provider "digitalocean" {
  token = var.digitalocean_token
}

# provider "mongodbatlas" {
#   public_key  = var.mongodb_public_key
#   private_key = var.mongodb_private_key
# }

resource "digitalocean_app" "app" {
  spec {
    name      = "web"
    region    = "nyc" # Choose your preferred region
    static_site {
      name            = "personal-website" # Add the required name argument
      build_command   = "pip install -r requirements.txt && gradio serve app.py"
      source_dir      = "."
      output_dir      = "public"
      github {
        repo   = "username/repo"
        branch = "main"
      }
    }

    env {
      key   = "OPENAI_API_KEY"
      value = var.openai_api_key
    }
  }
}

# resource "mongodbatlas_cluster" "main" {
#   project_id = var.mongodb_project_id
#   name       = "personal-db"
#   provider_instance_size_name = "M0" # Adjust size based on your needs
#   provider_name                = "AZURE"
#   provider_region_name         = "US_EAST_2" # Choose an appropriate Azure region
# }