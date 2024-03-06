provider "aws" {
  region = var.region_a
}

resource "aws_lightsail_key_pair" "ssh_key" {
  name = var.ssh-key-name
  public_key = var.ssh-key
}

resource "aws_lightsail_instance" "devcontainers-server" {
  availability_zone = var.availability_zone_a
  blueprint_id      = var.blueprint_id
  bundle_id         = var.bundle_id
  name              = var.devcontainer_server_name
  key_pair_name = aws_lightsail_key_pair.ssh_key.name
  tags = {
    "Name" = "DevContainers Server"
  }
  user_data = templatefile("${path.module}/install_docker.sh.tftpl", {
    server_user = "ubuntu"
    dependencies = [
      "docker-ce"
    , "wget"
    ]
  })
}