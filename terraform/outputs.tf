output "cluster_name" {
    value = google_container_cluster.gke_cluster.name
    description = "The name of the GKE cluster."
}

output "kubernetes_connection_command" {
    value = "gcloud container clusters get-credentials ${google_container_cluster.gke_cluster.name} --zone ${google_container_cluster.gke_cluster.location} --project ${var.project_id}"
    description = "The command to connect to the GKE cluster using kubectl."
}
