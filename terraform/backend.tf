terraform {
  backend "gcs" {
    bucket = "terraform-state-bjvc-test"
    prefix = "dev"
  }
}