variable "project_id" {
  description = "The ID of the project in which to create the resources."
  type        = string
}

variable "region" {
  description = "The region in which to create the resources."
  type        = string
}

variable "cluster_name" {
  description = "The name of the k8s cluster to create."
  type        = string
  default     = "hivebox-cluster"
}
