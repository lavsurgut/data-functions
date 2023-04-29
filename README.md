# data-gateway-functions
This is a small project that explores some ideas how one can write and read data from a Data Platform with Serverless Functions.
At the moment has just a single example of stream writing from an HTTP POST endpoint into the BigQuery.

## Functions
### Write HTTP POST requests data in BigQuery.
HTTP POST API provides a simple way to write data in BigQuery. New capabilities, like Storage Write API and GCP Cloud Functions Gen 2
allow to write small to medium amount of data without employing more sophisticated technology stack 
(e.g. GCP Dataflow/Apache Beam, Pub/Sub(or Kafka)).

#### Run locally for development
1. GCP credentials should be set in usual way via application-default credentials for your user account
   
   1.1 See https://cloud.google.com/docs/authentication/application-default-credentials#personal for details
2. Run below command to set up Flask service in the Debug mode with live code-reloading:
```
cd data_gateway/functions/bigquery/stream/writing && \
functions-framework --target bq_post --debug
```

#### Deployment
Deploy it to the Cloud Functions manually like in this example:
```
cd data_gateway/functions/bigquery/stream/writing && \
gcloud beta functions deploy bq-http-function \
--gen2 \
--cpu=1 \
--memory=256MiB \
--concurrency=1000 \
--max-instances=2 \
--runtime=python311 \
--region=<your_region> \
--source=. \
--entry-point=bq_post \
--trigger-http \
--project=<your_gcp_project> \
--allow-unauthenticated
```
Enable necessary GCP APIs if requested and IAM rights for the SA account Cloud Functions use to connect to BQ.

## Next steps
1. Allow to read data from BQ
2. Allow to read data from GCS
3. Make it work with AWS

