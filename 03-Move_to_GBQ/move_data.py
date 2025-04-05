import os
from google.cloud import storage, bigquery


def list_files_from_gcs(folder_name: str):
    storage_client = storage.Client()
    bucket_name = os.getenv("GCP_BUCKET_NAME")
    if bucket_name is None:
        raise Exception("GCP_BUCKET_NAME not found")
    bucket = storage_client.get_bucket(bucket_or_name=bucket_name)
    blobs = bucket.list_blobs(prefix=folder_name)
    for blob in blobs:
        yield blob.name


def load_parquet_to_bigquery(gcs_parquet_uri, dataset_id, table_id):
    """Loads Parquet files from GCS into BigQuery."""
    bigquery_client = bigquery.Client()
    table_ref = bigquery_client.dataset(dataset_id).table(table_id)

    # Set up the load job configuration
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        autodetect=True,  # Automatically detects the schema from the Parquet file
    )

    # Load the Parquet file into BigQuery
    load_job = bigquery_client.load_table_from_uri(
        gcs_parquet_uri, table_ref, job_config=job_config
    )

    # Wait for the load job to complete
    load_job.result()

    print(
        f"Loaded Parquet file from {gcs_parquet_uri} into BigQuery table {dataset_id}.{table_id}."
    )


if __name__ == "__main__":
    for file in list_files_from_gcs(folder_name="parquet"):
        load_parquet_to_bigquery(
            gcs_parquet_uri=f"gs://bucket-parking-transactions/{file}", dataset_id="parking_transactions", table_id="traffic"
        )
