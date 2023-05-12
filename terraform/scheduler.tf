resource "google_cloud_scheduler_job" "backup_scheduler" {
  name     = "backup-scheduler"
  schedule = "0 12 * * 1"
  time_zone = "America/New_York"

  http_target {
    uri         = google_cloudfunctions_function.backup_gcf.https_trigger_url
    http_method = "POST"
    oidc_token {
      service_account_email = "bjvc-externo@green-device-382800.iam.gserviceaccount.com"
    }
    body        = base64encode("{\"key\":\"exec\"}")

    headers = {
      Content-Type = "application/json"
    }

  }
}

resource "google_cloud_scheduler_job" "restore_scheduler" {
  name     = "restore-scheduler"
  schedule = "0 0 1 1 *"
  time_zone = "America/New_York"

  http_target {
    uri         = google_cloudfunctions_function.restore_gcf.https_trigger_url
    http_method = "POST"
    oidc_token {
      service_account_email = "bjvc-externo@green-device-382800.iam.gserviceaccount.com"
    }
    body        = base64encode("{\"table_name\":\"hired_employees\"}")

    headers = {
      Content-Type = "application/json"
    }

  }
}