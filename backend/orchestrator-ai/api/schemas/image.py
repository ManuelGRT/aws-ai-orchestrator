from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

#################
# UPLOAD IMAGE
#################
'''
class UploadImageOutput(BaseModel):
    """
    Update step output fields
    """
    success: bool = Field(description='Success', example='')    
    message: str = Field(description='Message Success', example='')    
    image_id: str = Field(default=None, description='Images Id')
'''
class UploadImageOutput(BaseModel):
    """
    Update step output fields
    """
    success: bool = Field(description='Success')    
    message: str = Field(description='Message Success')    
    image_id: str = Field(default=None, description='Image Id')