## local variable
locals {
  timestamp = formatdate("YYMMDDhhmmss", timestamp())
  root_dir_gcf = abspath("../gcf/")
}

#======== gcf_instance_http ==========
# Compress source code
data "archive_file" "http_zip_file" {
  type        = "zip"
  output_path = "/tmp/http_gcf.zip"
  source_dir  = "${local.root_dir_gcf}/rest-api/src"
}
# Add source code zip to bucket
resource "google_storage_bucket_object" "http_zip_object" { 
  name   = "gcf_zip_files/rest_api/${data.archive_file.http_zip_file.output_md5}.zip"
  bucket = google_storage_bucket.artifacts_bucket.name
  source = data.archive_file.http_zip_file.output_path
  depends_on = [data.archive_file.http_zip_file]
}
# Add source instance
resource "google_cloudfunctions_function" "http_gcf" {

  name        = "rest-api-function"
  runtime     = "python310"
  entry_point = "main"
  source_archive_bucket = google_storage_bucket.artifacts_bucket.name
  source_archive_object = google_storage_bucket_object.http_zip_object.name

  trigger_http = true

  depends_on = [google_storage_bucket_object.http_zip_object]
}

#======== gcf_instance_csv_migration ==========
# Compress source code
data "archive_file" "csv_migration_zip_file" {
  type        = "zip"
  output_path = "/tmp/csv_migration_gcf.zip"
  source_dir  = "${local.root_dir_gcf}/csv-migration/src"
}
# Add source code zip to bucket
resource "google_storage_bucket_object" "csv_migration_zip_object" { 
  name   = "gcf_zip_files/csv_migration/${data.archive_file.csv_migration_zip_file.output_md5}.zip"
  bucket = google_storage_bucket.artifacts_bucket.name
  source = data.archive_file.csv_migration_zip_file.output_path
  depends_on = [data.archive_file.csv_migration_zip_file]
}
# Add source instance
resource "google_cloudfunctions_function" "csv_migration_gcf" {

  name        = "csv-migration-function"
  runtime     = "python310"
  entry_point = "main"
  source_archive_bucket = google_storage_bucket.artifacts_bucket.name
  source_archive_object = google_storage_bucket_object.csv_migration_zip_object.name

  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = google_storage_bucket.data_bucket.name
  }

  depends_on = [google_storage_bucket_object.csv_migration_zip_object]
}

#======== gcf_instance_backup ==========
# Compress source code
data "archive_file" "backup_zip_file" {
  type        = "zip"
  output_path = "/tmp/backup_gcf.zip"
  source_dir  = "${local.root_dir_gcf}/backup-process/src"
}
# Add source code zip to bucket
resource "google_storage_bucket_object" "backup_zip_object" { 
  name   = "gcf_zip_files/rest_api/${data.archive_file.backup_zip_file.output_md5}.zip"
  bucket = google_storage_bucket.artifacts_bucket.name
  source = data.archive_file.backup_zip_file.output_path
  depends_on = [data.archive_file.backup_zip_file]
}
# Add source instance
resource "google_cloudfunctions_function" "backup_gcf" {

  name        = "backup-process-function"
  runtime     = "python310"
  entry_point = "main"
  source_archive_bucket = google_storage_bucket.artifacts_bucket.name
  source_archive_object = google_storage_bucket_object.backup_zip_object.name

  trigger_http = true

  depends_on = [google_storage_bucket_object.backup_zip_object]
}

#======== gcf_instance_restore ==========
# Compress source code
data "archive_file" "restore_zip_file" {
  type        = "zip"
  output_path = "/tmp/restore_gcf.zip"
  source_dir  = "${local.root_dir_gcf}/restore-process/src"
}
# Add source code zip to bucket
resource "google_storage_bucket_object" "restore_zip_object" { 
  name   = "gcf_zip_files/rest_api/${data.archive_file.restore_zip_file.output_md5}.zip"
  bucket = google_storage_bucket.artifacts_bucket.name
  source = data.archive_file.restore_zip_file.output_path
  depends_on = [data.archive_file.restore_zip_file]
}
# Add source instance
resource "google_cloudfunctions_function" "restore_gcf" {

  name        = "restore-process-function"
  runtime     = "python310"
  entry_point = "main"
  source_archive_bucket = google_storage_bucket.artifacts_bucket.name
  source_archive_object = google_storage_bucket_object.restore_zip_object.name

  trigger_http = true

  depends_on = [google_storage_bucket_object.restore_zip_object]
}

#======== gcf_instance_end_point ==========
# Compress source code
data "archive_file" "end_point_zip_file" {
  type        = "zip"
  output_path = "/tmp/end_point_gcf.zip"
  source_dir  = "${local.root_dir_gcf}/end-point-requirement/src"
}
# Add source code zip to bucket
resource "google_storage_bucket_object" "end_point_zip_object" { 
  name   = "gcf_zip_files/rest_api/${data.archive_file.end_point_zip_file.output_md5}.zip"
  bucket = google_storage_bucket.artifacts_bucket.name
  source = data.archive_file.end_point_zip_file.output_path
  depends_on = [data.archive_file.end_point_zip_file]
}
# Add source instance
resource "google_cloudfunctions_function" "end_point_gcf" {

  name        = "end_point-requirement-function"
  runtime     = "python310"
  entry_point = "main"
  source_archive_bucket = google_storage_bucket.artifacts_bucket.name
  source_archive_object = google_storage_bucket_object.end_point_zip_object.name

  trigger_http = true

  depends_on = [google_storage_bucket_object.end_point_zip_object]
}

#======= Output cloud funtcions url ==============

output "http_function_url" {
  value = google_cloudfunctions_function.http_gcf.https_trigger_url
}

output "csv_migration_function_url" {
  value = google_cloudfunctions_function.csv_migration_gcf.https_trigger_url
}

output "backup_function_url" {
  value = google_cloudfunctions_function.backup_gcf.https_trigger_url
}

output "restore_function_url" {
  value = google_cloudfunctions_function.restore_gcf.https_trigger_url
}
