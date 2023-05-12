
resource "google_storage_bucket" "data_bucket" {
  name          = "data-bjvc-test"
  location      = "US"
}

resource "google_storage_bucket" "artifacts_bucket" {
  name          = "artifacts-bjvc-test"
  location      = "US"
}
