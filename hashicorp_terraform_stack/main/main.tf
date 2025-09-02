
module "networking" {
  source = "../networking"
}

module "iam" {
  source = "../iam"
}

module "compute" {
  source = "../compute"
}

module "storage" {
  source = "../storage"
}

module "observability" {
  source = "../observability"
}

module "secrets" {
  source = "../secrets"
}

module "consul" {
  source = "../consul"
}
