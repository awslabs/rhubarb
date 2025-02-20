# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import re
import inspect
import logging
from typing import Dict, List, Tuple, Callable, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SubParameter(BaseModel):
    name: str
    type: str
    description: str
    is_optional: bool = False

    @property
    def json_type(self) -> str:
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "dict": "object",
            "list": "array",
        }
        return type_mapping.get(self.type, "string")


class Parameter(BaseModel):
    name: str
    type: str
    description: str
    is_optional: bool = False
    properties: Dict[str, SubParameter] = {}
    required_subparameters: List[str] = []

    @property
    def json_type(self) -> str:
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "dict": "object",
            "list": "array",
        }
        return type_mapping.get(self.type, "string")


class ToolsSyndicate:
    def __init__(self, func: Callable):
        self.func = func
        self.func_name = f"{func.__name__}_tool"
        self.docstring = inspect.getdoc(func)
        if not self.docstring:
            logger.error(f"Tool Function '{func.__name__}' must have a docstring.")
            raise ValueError(f"Tool Function '{func.__name__}' must have a docstring.")
        self.description: str = ""
        self.parameters: Dict[str, Parameter] = {}
        self.required_parameters: List[str] = []
        self._validate_signature()

    def _validate_signature(self):
        sig = inspect.signature(self.func)
        return_annotation = sig.return_annotation
        params = list(sig.parameters.values())

        if len(params) != 1:
            logger.error(f"Tool function '{self.func.__name__}' must have exactly one parameter.")
            raise ValueError(
                f"Tool function '{self.func.__name__}' must have exactly one parameter."
            )
        param = params[0]
        # If type is specified, it must be dict
        if param.annotation is not inspect.Parameter.empty and param.annotation != dict:
            logger.error(
                f"Tool function '{self.func.__name__}' parameter '{param.name}' must be of type 'dict'."
            )
            raise ValueError(
                f"Tool function '{self.func.__name__}' parameter '{param.name}' must be of type 'dict'."
            )

        if return_annotation is inspect.Signature.empty:
            logger.error(
                f"Tool function '{self.func.__name__}' must have a return type annotation."
            )
            raise ValueError(
                f"Tool function '{self.func.__name__}' must have a return type annotation."
            )

        # Allowed return types
        allowed_types = {str, dict}

        # Handle cases where return_annotation is None
        if return_annotation is None:
            logger.error(
                f"Tool function '{self.func.__name__}' has an invalid return type 'None'. Allowed types are 'str' or 'dict'."
            )
            raise ValueError(
                f"Tool function '{self.func.__name__}' has an invalid return type 'None'. Allowed types are 'str' or 'dict'."
            )

        # Handle typing.Optional and other complex return types
        if hasattr(return_annotation, "__origin__"):
            origin_type = return_annotation.__origin__
            if origin_type not in allowed_types:
                logger.error(
                    f"Tool function '{self.func.__name__}' has an invalid return type '{return_annotation}'. Allowed types are 'str' or 'dict'."
                )
                raise ValueError(
                    f"Tool function '{self.func.__name__}' has an invalid return type '{return_annotation}'. Allowed types are 'str' or 'dict'."
                )
        elif return_annotation not in allowed_types:
            # For built-in types and classes
            type_name = getattr(return_annotation, "__name__", str(return_annotation))
            logger.error(
                f"Tool function '{self.func.__name__}' has an invalid return type '{type_name}'. Allowed types are 'str' or 'dict'."
            )
            raise ValueError(
                f"Tool function '{self.func.__name__}' has an invalid return type '{type_name}'. Allowed types are 'str' or 'dict'."
            )

    def _parse_type(self, type_str: str) -> (bool, str):
        type_str = type_str.strip()
        is_optional = False
        if type_str.startswith("Optional[") and type_str.endswith("]"):
            is_optional = True
            base_type = type_str[9:-1]
        elif type_str.startswith("Optional"):
            is_optional = True
            base_type = type_str[len("Optional") :].strip("[]")
        else:
            base_type = type_str
        return is_optional, base_type

    def _parse_docstring(self):
        lines = self.docstring.split("\n")
        lines = [line.rstrip() for line in lines]
        index = 0
        # Skip initial blank lines
        while index < len(lines) and not lines[index].strip():
            index += 1
        # Collect description
        description_lines = []
        while index < len(lines) and not lines[index].strip().startswith(
            ("Args:", "Returns:", "Raises:", "Examples:", "Notes:", "References:")
        ):
            description_lines.append(lines[index])
            index += 1
        self.description = " ".join(description_lines).strip()
        if not self.description:
            logger.error(
                f"Docstring for tool function '{self.func.__name__}' must have a description."
            )
            raise ValueError(
                f"Docstring for tool function '{self.func.__name__}' must have a description."
            )
        # Find 'Args:' section
        while index < len(lines) and lines[index].strip() != "Args:":
            index += 1
        if index >= len(lines):
            logger.error(
                f"Docstring for tool function '{self.func.__name__}' must have an 'Args:' section."
            )
            raise ValueError(
                f"Docstring for tool function '{self.func.__name__}' must have an 'Args:' section."
            )
        index += 1  # Skip 'Args:' line

        current_param: Optional[Parameter] = None
        arg_pattern = re.compile(r"^ {0,4}(\w+)\(([^)]+)\): (.+)")
        sub_arg_pattern = re.compile(r"^ {0,8}- (\w+)\(([^)]+)\): (.+)")

        while index < len(lines):
            line = lines[index]
            stripped_line = line.strip()
            # Stop parsing if we reach another section
            if stripped_line in ("Returns:", "Raises:", "Examples:", "Notes:", "References:"):
                break
            if not stripped_line:
                index += 1
                continue
            arg_match = arg_pattern.match(line)
            sub_arg_match = sub_arg_pattern.match(line)
            if arg_match:
                param_name, param_type, param_desc = arg_match.groups()
                is_optional, base_type = self._parse_type(param_type)
                if not base_type:
                    logger.error(
                        f"Type not specified for parameter '{param_name}' in tool function '{self.func.__name__}'."
                    )
                    raise ValueError(
                        f"Type not specified for parameter '{param_name}' in tool function '{self.func.__name__}'."
                    )
                param = Parameter(
                    name=param_name,
                    type=base_type,
                    description=param_desc.strip(),
                    is_optional=is_optional,
                    properties={},
                    required_subparameters=[],
                )
                self.parameters[param_name] = param
                current_param = param
                if not is_optional:
                    self.required_parameters.append(param_name)
            elif sub_arg_match and current_param:
                sub_param_name, sub_param_type, sub_param_desc = sub_arg_match.groups()
                is_optional, base_type = self._parse_type(sub_param_type)
                if not base_type:
                    logger.error(
                        f"Type not specified for sub-parameter '{sub_param_name}' of '{current_param.name}' in tool function '{self.func.__name__}'."
                    )
                    raise ValueError(
                        f"Type not specified for sub-parameter '{sub_param_name}' of '{current_param.name}' in tool function '{self.func.__name__}'."
                    )
                sub_param = SubParameter(
                    name=sub_param_name,
                    type=base_type,
                    description=sub_param_desc.strip(),
                    is_optional=is_optional,
                )
                current_param.properties[sub_param_name] = sub_param
                if not is_optional:
                    current_param.required_subparameters.append(sub_param_name)
            else:
                logger.error(
                    f"Invalid line in docstring: '{line.strip()}' in tool function '{self.func.__name__}'."
                )
                raise ValueError(
                    f"Invalid line in docstring: '{line.strip()}' in tool function '{self.func.__name__}'."
                )
            index += 1

    def _generate_schema(self) -> Dict:
        json_properties = {}
        for param in self.parameters.values():
            prop = {"type": param.json_type, "description": param.description}
            if param.json_type == "object" and param.properties:
                prop["properties"] = {}
                for sub_param in param.properties.values():
                    sub_prop = {"type": sub_param.json_type, "description": sub_param.description}
                    prop["properties"][sub_param.name] = sub_prop
                if param.required_subparameters:
                    prop["required"] = param.required_subparameters
            json_properties[param.name] = prop

        json_schema = {
            "toolSpec": {
                "name": self.func_name,
                "description": self.description,
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": json_properties,
                        "required": self.required_parameters,
                    }
                },
            }
        }
        return json_schema

    @classmethod
    def generate_tool_config(
        cls, functions_list: List[Callable]
    ) -> Tuple[Dict, Dict[str, Callable]]:
        """
        Generate schemas for a list of functions.

        Args:
            functions_list (List[Callable]): List of functions to process.

        Returns:
            Tuple:
            - Dictionary containing a list of schemas under the key 'tools'.
            - Dictionary containing the tool functions
        """
        schemas = []
        tool_functions = {}
        for func in functions_list:
            try:
                generator = cls(func)
                generator._parse_docstring()
                schema = generator._generate_schema()
                schemas.append(schema)
                tool_functions[func.__name__] = func
            except ValueError as e:
                print(f"Error processing function '{func.__name__}': {e}")
        return {"tools": schemas}, tool_functions
