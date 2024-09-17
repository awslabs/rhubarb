from typing import List

from pydantic import Field, BaseModel, GetJsonSchemaHandler
from pydantic_core import core_schema as cs


# Default model
class DefaultModel(BaseModel):
    page: int = Field(..., title="page", description="The page number of the document")
    detected_languages: List[str] = Field(
        ...,
        title="detected_languages",
        description="The language, example English, Spanish, Italian, Chinese, German etc.",
    )
    content: str = Field(..., title="content", description="Your response")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ):
        schema = handler(core_schema)
        schema = handler.resolve_ref_schema(schema)
        del schema["title"]
        return {
            "type": "array",
            "description": "A document with one or more pages",
            "items": schema,
        }


# Chat model
class ChatModel(BaseModel):
    text: str = Field(..., description="Your friendly and accurate response", title="text")
    sources: List[int] = Field(
        default=[],
        title="sources",
        description="Page numbers of the document which were used to form the answer",
    )
    quotes: List[str] = Field(
        default=[],
        title="quotes",
        description="The various quotes from the document which relates to the answer.",
    )


# Figure model
class FigureModel(BaseModel):
    page: int = Field(..., title="page", description="The page number of the document")
    figure_analysis: str = Field(..., title="figure_analysis", description="Your response")
    figure_description: str = Field(
        title="figure_description",
        description="The verbatim description of the image if specified in the document.",
    )
    reasoning: str = Field(
        title="reasoning", description="A step-by-step explanation of your final analysis."
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ):
        schema = handler(core_schema)
        schema = handler.resolve_ref_schema(schema)
        schema["required"] = ["page", "figure_analysis"]
        del schema["title"]
        return {
            "type": "array",
            "description": "A document with one or more pages",
            "items": schema,
        }


# Document classification model
class ClassificationModel(BaseModel):
    page: int = Field(..., title="page", description="The page number of the document")
    class_: str = Field(
        ..., title="class", description="The class this page belongs to.", alias="class"
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ):
        schema = handler(core_schema)
        schema = handler.resolve_ref_schema(schema)
        del schema["title"]
        return {
            "type": "array",
            "description": "A document with one or more pages",
            "items": schema,
        }


# Multi-class Document classification model
class MultiClassModel(BaseModel):
    page: int = Field(..., title="page", description="The page number of the document")
    class_: List[str] = Field(
        ..., title="class", description="The classes the page may belong to.", alias="class"
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ):
        schema = handler(core_schema)
        schema = handler.resolve_ref_schema(schema)
        del schema["title"]
        return {
            "type": "array",
            "description": "A document with one or more pages, where each page belongs to one or more class",
            "items": schema,
        }


# Name Entity Recognition Model
class NERModel(BaseModel):
    page: int = Field(..., title="page", description="The page number of the document")
    entities: List[dict] = Field(
        ..., title="entities", description="Common named entities found in this page"
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ):
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema["properties"]["entities"]["items"]["oneOf"] = []
        del json_schema["title"]
        return {"type": "array", "items": json_schema}
