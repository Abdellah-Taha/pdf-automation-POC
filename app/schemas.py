from pydantic import BaseModel, Field
from datetime import date

class Schema(BaseModel):
    document_type: str = Field(pattern="^(invoice|receipt|contract|other)$", description="Type of the document")
    supplier: str = Field(..., description="Name of the supplier")
    document_date: date = Field(..., description="Date of the document")
    suggestion_filename: str = Field(pattern=r"\.pdf$", description="Suggested filename for the document")
    destination_path: str = Field(..., description="Destination path for the document")

