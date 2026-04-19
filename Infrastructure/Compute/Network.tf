resource "google_compute_network" "main_vpc" {
  name = var.cliniclarity_vpc
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "private_subnet" {
  name = var.cliniclarity_subnet
  ip_cidr_range = "10.0.0.0/28"
  region = var.region
  network = google_compute_network.main_vpc.id
  private_ip_google_access = true
}

resource "google_compute_address" "nat_ip" {
  name = "cliniclarity-nat-ip"
  region = var.region
}

resource "google_compute_router" "router" {
  name = "cliniclarity-router"
  region = var.region
  network = google_compute_network.main_vpc.id
}

resource "google_compute_router_nat" "nat_gateway" {
  name = "cliniclarity-nat-gateway"
  router = google_compute_router.router.name
  region = google_compute_router.router.region
  nat_ip_allocate_option = "MANUAL_ONLY"
  nat_ips = [google_compute_address.nat_ip.self_link]
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}