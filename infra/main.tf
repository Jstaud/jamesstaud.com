# main.tf
provider "digitalocean" {
  token = var.digitalocean_token
}

# provider "mongodbatlas" {
#   public_key  = var.mongodb_public_key
#   private_key = var.mongodb_private_key
# }

provider "cloudflare" {
  email   = var.cloudflare_email
  api_key = var.cloudflare_api_key
}

resource "digitalocean_app" "app" {
  spec {
    name      = "web"
    region    = "nyc" # Choose your preferred region
    static_site {
      name            = "jamesstaud.com" # Add the required name argument
      build_command   = "pip install -r requirements.txt && gradio serve app.py"
      source_dir      = "frontend"
      output_dir      = "public"
      github {
        repo   = "jstaud/jamesstaud.com"
        branch = "main"
      }
    }

    env {
      key   = "OPENAI_API_KEY"
      value = var.openai_api_key
    }

    env {
      key   = "BACKEND_API_URL"
      value = "http://backend.jamesstaud.com:8000/query"
    }
  }
}

resource "digitalocean_app" "backend" {
  spec {
    name      = "backend"
    region    = "nyc" # Choose your preferred region
    service {
      name = "backend-service"
      run_command = "uvicorn main:app --host 0.0.0.0 --port 8000"
      source_dir = "backend"
      github {
        repo   = "jstaud/jamesstaud.com"
        branch = "main"
      }
      http_port = 8000
    }
  }
}

# Can't provision M0 clusters using Terraform
# resource "mongodbatlas_cluster" "main" {
#   project_id = var.mongodb_project_id
#   name       = "personal-db"
#   provider_instance_size_name = "M0" # Adjust size based on your needs
#   provider_name                = "AZURE"
#   provider_region_name         = "US_EAST_2" # Choose an appropriate Azure region
# }

# Cloudflare DNS Records
resource "cloudflare_record" "backend" {
  zone_id = var.cloudflare_zone_id
  name    = "backend"
  value   = digitalocean_droplet.backend.ipv4_address
  type    = "A"
  ttl     = 3600
  proxied = true
}

resource "cloudflare_record" "www" {
  zone_id = var.cloudflare_zone_id
  name    = "www"
  value   = digitalocean_app.app.default_ingress
  type    = "CNAME"
  ttl     = 3600
  proxied = true
}

resource "cloudflare_record" "root" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  value   = digitalocean_app.app.default_ingress
  type    = "CNAME"
  ttl     = 3600
  proxied = true
}