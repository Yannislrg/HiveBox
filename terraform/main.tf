resource "google_compute_network" "vpc_network" {
    name                    = "hivebox-vpc"
    auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
    name          = "hivebox-subnet"
    ip_cidr_range = "10.0.1.0/24"
    region        = var.region
    network       = google_compute_network.vpc_network.id
}

resource "google_container_cluster" "gke_cluster" {
    name    = var.cluster_name
    location = "${var.region}-a"
    network = google_compute_network.vpc_network.name
    subnetwork = google_compute_subnetwork.subnet.name
    remove_default_node_pool = true
    initial_node_count = 1
    addons_config {
        http_load_balancing {
            disabled = false
        }
    }
    private_cluster_config {
        enable_private_nodes    = true
        enable_private_endpoint = false
    }
}

resource "google_container_node_pool" "primary_nodes" {
    name = "hivebox-node-pool"
    location = "${var.region}-a"
    cluster = google_container_cluster.gke_cluster.name
    node_count = 1

    node_config {
        preemptible = true
        machine_type = "e2-small"
        labels = {
            env = "dev"
        }

        oauth_scopes = [
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
        ]
    }
}

