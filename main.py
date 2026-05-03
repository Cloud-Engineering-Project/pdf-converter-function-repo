import base64
import json
import os
import uuid
from io import BytesIO

from PIL import Image
from google.cloud import storage
from google.cloud import pubsub_v1

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
CONVERTED_BUCKET = os.environ["CONVERTED_BUCKET"]
FILE_CONVERTED_TOPIC = os.environ.get("FILE_CONVERTED_TOPIC", "file-converted")

storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()


def pdf_converter(event, context):
    message_data = base64.b64decode(event["data"]).decode("utf-8")
    payload = json.loads(message_data)

    email = payload["email"]
    filename = payload["filename"]
    file_base64 = payload["file_base64"]

    original_bytes = base64.b64decode(file_base64)

    image = Image.open(BytesIO(original_bytes)).convert("RGB")

    output_buffer = BytesIO()
    image.save(output_buffer, format="PDF")
    converted_bytes = output_buffer.getvalue()

    converted_base64 = base64.b64encode(converted_bytes).decode("utf-8")

    output_filename = f"{uuid.uuid4()}.pdf"
    object_name = f"converted/{output_filename}"

    bucket = storage_client.bucket(CONVERTED_BUCKET)
    blob = bucket.blob(object_name)

    blob.upload_from_string(
        converted_base64,
        content_type="text/plain"
    )

    converted_event = {
        "email": email,
        "original_filename": filename,
        "output_filename": output_filename,
        "output_type": "pdf",
        "bucket": CONVERTED_BUCKET,
        "object": object_name,
        "content_type": "application/pdf",
    }

    topic_path = publisher.topic_path(PROJECT_ID, FILE_CONVERTED_TOPIC)
    publisher.publish(topic_path, json.dumps(converted_event).encode("utf-8"))