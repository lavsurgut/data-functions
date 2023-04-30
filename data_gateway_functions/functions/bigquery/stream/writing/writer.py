from contextlib import contextmanager
from typing import Any, Iterable

from google.cloud.bigquery_storage import BigQueryWriteClient
from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1.writer import AppendRowsStream, AppendRowsFuture
from google.protobuf import descriptor_pb2
from google.protobuf.descriptor import Descriptor
from google.protobuf.message import Message

stream_dict = dict()


def write(client: BigQueryWriteClient,
          destination: str,
          request: Message) -> AppendRowsFuture:
    with stream_context(client, request.DESCRIPTOR, destination) as stream:
        return write_with_append_stream(stream, [request])


@contextmanager
def stream_context(client, descriptor, stream_name) -> AppendRowsStream:
    stream = stream_dict.get(stream_name)
    try:
        if stream is None:
            stream = init_stream(client,
                                 stream_name,
                                 descriptor
                                 )
            stream_dict[stream_name] = stream
        yield stream
    except:
        if stream is not None:
            stream.close()
        stream_dict[stream_name] = None


def init_stream(
        client: BigQueryWriteClient,
        stream_name: str,
        message_protobuf_descriptor: Descriptor) -> AppendRowsStream:
    request_template = types.AppendRowsRequest()
    request_template.write_stream = stream_name
    proto_schema = types.ProtoSchema()
    proto_descriptor = descriptor_pb2.DescriptorProto()
    message_protobuf_descriptor.CopyToProto(proto_descriptor)
    proto_schema.proto_descriptor = proto_descriptor
    proto_data = types.AppendRowsRequest.ProtoData()
    proto_data.writer_schema = proto_schema
    request_template.proto_rows = proto_data
    return AppendRowsStream(
        client, request_template
    )


def get_destination(project_id: str,
                    dataset_id: str,
                    table_id: str) -> str:
    return f"projects/{project_id}/datasets/{dataset_id}/tables/{table_id}/streams/_default"


def write_with_append_stream(
        append_rows_stream: AppendRowsStream,
        pb_rows: Iterable[Any]) -> AppendRowsFuture:
    proto_rows = types.ProtoRows()
    for row in pb_rows:
        proto_rows.serialized_rows.append(row.SerializeToString())
    proto_data = types.AppendRowsRequest.ProtoData()
    proto_data.rows = proto_rows
    request = types.AppendRowsRequest()
    request.proto_rows = proto_data
    return append_rows_stream.send(request)
