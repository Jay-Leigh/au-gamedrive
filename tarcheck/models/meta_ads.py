from pydantic import BaseModel, Field, ConfigDict
from typing import List, Any

class MetaSession(BaseModel):
    session_id: int
    batch_seq: int
    last_batch_flag: bool
    estimated_num_total: int

class MetaPayloadData(BaseModel):
    schema_keys: List[str] = Field(alias="schema")
    data: List[List[Any]]
    model_config = ConfigDict(populate_by_name=True) ## config at top


class MetaBatchPayload(BaseModel):
    audience_id: str
    session: MetaSession
    payload: MetaPayloadData