output "public_ip" {
  value = aws_lightsail_instance.devcontainers-server.public_ip_address
}