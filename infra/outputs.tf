# outputs.tf
output "backend_ip" {
  value = digitalocean_droplet.backend.ipv4_address
}

output "frontend_url" {
  value = digitalocean_app.app.default_ingress
}