import json

import functions_framework
import pendulum
from google.cloud.bigquery_storage import BigQueryWriteClient
from werkzeug.exceptions import BadRequest

from proto_declaration.request_pb2 import Request
from writer import write, get_destination

client = BigQueryWriteClient()


@functions_framework.http
def bq_post(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    if request.method != "POST":
        raise BadRequest("Only POST methods allowed")
    # this also tries to parse json and raise an error if it didn't work
    event_raw = dict(request.get_json())
    ts = pendulum.now(tz="UTC")
    ts_in_micro = int(ts.float_timestamp * 1000 * 1000)
    event = {
        "data": {
            "req_body": event_raw},
        "header": {
            "timestamp": ts.to_iso8601_string()
        }
    }
    event_str = json.dumps(event)
    req = Request(created_at=ts_in_micro,
                  event=event_str)
    destination = get_destination("your-gcp-project-id",
                                  "dataset-id",
                                  "table-name")
    write(client, destination, req)
    return "Successfully sent an event"
