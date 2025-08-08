from typing import Annotated
from pydantic import BeforeValidator, BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    """
    Container for a single student record.
    """

    # The primary key for the StudentModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    provider: str = Field(...)
    provider_id: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "provider": "google",
                "provider_id": "1234567890",
            }
        },
    )

class UpdateUserModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
            }
        },
    )
    
class UserCollection(BaseModel):
    """
    A container holding a list of `UserModel` instances.
    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """
    users: List[UserModel]