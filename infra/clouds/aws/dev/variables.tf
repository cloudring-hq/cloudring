variable "ssh-key" {
  description = "User ssh key"
  type = string
}

variable "server_user" {
  description = "Server user name"
  type = string
}

variable "ssh-key-name" {
  description = "User ssh key"
  type = string
}

variable "region_a" {
  description = "The infrastructure zone A"
  type = string
}

variable "availability_zone_a" {
  description = "The availability zone in which to launch the server"
  type        = string
}

variable "blueprint_id" {
  description = "The ID of the blueprint (image) for the instance"
  type        = string
}

variable "bundle_id" {
  description = "The bundle ID for the instance size/configuration"
  type        = string
}

variable "devcontainer_server_name" {
  description = "The name of the Lightsail instance"
  type        = string
}

