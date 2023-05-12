terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.62.1"
    }

    archive = {
      source = "hashicorp/archive"
      version = "2.3.0"
    }
  }
}

provider "google" {
  # Set your project, region, and zone here
  project = "green-device-382800"
  region  = "us-central1"
}

