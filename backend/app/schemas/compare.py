import uuid

from pydantic import BaseModel


class CompareIn(BaseModel):
    document_a_id: uuid.UUID
    document_b_id: uuid.UUID
