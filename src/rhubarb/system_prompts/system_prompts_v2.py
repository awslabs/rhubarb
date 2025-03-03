import os
import json
from typing import List
from datetime import datetime

from rhubarb.models import LanguageModels
from rhubarb.schema_factory import SchemaFactory


class SystemPrompts:
    def __init__(
        self,
        model_id: LanguageModels = LanguageModels.CLAUDE_SONNET_V2,
        entities: List[dict] = None,
        streaming: bool = False,
    ):
        self.model_id = model_id
        self.entities = entities
        self.streaming = streaming
        self.dt = datetime.now().strftime("%b-%m-%Y")
        self.sf = SchemaFactory()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        sys_prompt_file_path = os.path.join(BASE_DIR, "sysprompts", "prompts.json")
        with open(sys_prompt_file_path, "r") as f:
            self.prompts = json.load(f)

    def _get_model_name(self) -> str:
        if (
            self.model_id == LanguageModels.CLAUDE_OPUS_V1
            or self.model_id == LanguageModels.CLAUDE_HAIKU_V1
            or self.model_id == LanguageModels.CLAUDE_SONNET_V1
            or self.model_id == LanguageModels.CLAUDE_SONNET_V2
        ):
            return "anthropic"
        elif self.model_id == LanguageModels.NOVA_LITE or self.model_id == LanguageModels.NOVA_PRO:
            return "nova"

    def get_prompt(self, prompt_name: str) -> str:
        if prompt_name not in self.prompts:
            raise ValueError(f"Unknown prompt name: {prompt_name}")

        model_name = self._get_model_name()
        prompt_data = self.prompts[prompt_name]

        if model_name not in prompt_data:
            raise ValueError(f"No prompt available for model ID: {self.model_id}")

        model_prompt = prompt_data[model_name]
        content = model_prompt["content"]

        if prompt_name == "NERSysPrompt":
            ner_schema = getattr(self.sf, model_prompt["schema_name"])
            ner_schema["items"]["properties"]["entities"]["items"]["oneOf"] = self.entities
            schema_str = json.dumps(ner_schema)
            content = content.format(dt=self.dt, schema=schema_str)
        elif prompt_name == "SchemaGenSysPromptWithRephrase":
            schema = getattr(self.sf, model_prompt["schema_name"])
            rephrase_schema = {
                "type": "object",
                "properties": {
                    "rephrased_question": {
                        "type": "string",
                        "description": "User's rephrased question",
                    },
                    "output_schema": schema,
                },
            }
            schema_str = json.dumps(rephrase_schema)
            content = content.format(dt=self.dt, schema=schema_str)
        else:
            if model_prompt.get("requires_schema", False):
                schema = json.dumps(getattr(self.sf, model_prompt["schema_name"]))
                schema_str = json.dumps(schema)
                content = content.format(dt=self.dt, schema=schema_str)
            else:
                content = content.format(dt=self.dt)
        return content

    @property
    def DefaultSysPrompt(self):
        return self.get_prompt("DefaultSysPrompt")

    @property
    def SchemaSysPrompt(self):
        return self.get_prompt("SchemaSysPrompt")

    @property
    def ChatSysPrompt(self):
        return self.get_prompt("ChatSysPrompt")

    @property
    def SummarySysPrompt(self):
        return self.get_prompt("SummarySysPrompt")

    @property
    def FigureSysPrompt(self):
        return self.get_prompt("FigureSysPrompt")

    @property
    def NERSysPrompt(self):
        if not self.entities:
            raise ValueError("Entities list required")
        return self.get_prompt("NERSysPrompt")

    @property
    def SchemaGenSysPrompt(self):
        return self.get_prompt("SchemaGenSysPrompt")

    @property
    def SchemaGenSysPromptWithRephrase(self):
        return self.get_prompt("SchemaGenSysPromptWithRephrase")

    @property
    def ClassificationSysPrompt(self):
        return self.get_prompt("ClassificationSysPrompt")

    @property
    def MultiClassificationSysPrompt(self):
        return self.get_prompt("MultiClassificationSysPrompt")
