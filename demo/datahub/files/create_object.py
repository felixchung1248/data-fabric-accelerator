# Inlined from /metadata-ingestion/examples/library/create_tag.py
import logging
import os

from datahub.emitter.mce_builder import make_tag_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Imports for metadata model classes
from datahub.metadata.schema_classes import TagPropertiesClass

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
datahub_url = os.environ['DATAHUB_URL']

tag_urn = make_tag_urn("sensitive")
tag_properties_aspect = TagPropertiesClass(
    name="sensitive",
    description="Having this tag means this column or table contains sensitive data.",
)

event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
    entityUrn=tag_urn,
    aspect=tag_properties_aspect,
)

# Create rest emitter
rest_emitter = DatahubRestEmitter(gms_server=datahub_url)
rest_emitter.emit(event)
log.info(f"Created tag {tag_urn}")
