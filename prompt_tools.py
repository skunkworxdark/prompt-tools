# 2023 skunkworxdark (https://github.com/skunkworxdark)

import csv
import io
import json
import random
import re
from typing import Literal, Optional, Union

from pydantic import BaseModel

from invokeai.invocation_api import (
    SCHEDULER_NAME_VALUES,
    BaseInvocation,
    BaseInvocationOutput,
    FieldDescriptions,
    Input,
    InputField,
    InvocationContext,
    OutputField,
    StringOutput,
    UIComponent,
    invocation,
    invocation_output,
)


def csv_line_to_list(csv_string: str) -> list[str]:
    """Converts the first line of a CSV into a list of strings"""
    with io.StringIO(csv_string) as input:
        reader = csv.reader(input)
        return next(reader)


# not currently used but kept just incase
def csv_to_list(csv_string: str) -> list[list[str]]:
    """Converts a CSV into a list of list of strings"""
    with io.StringIO(csv_string) as input:
        reader = csv.reader(input)
        return list(reader)


def list_to_csv(strings: list[str]) -> str:
    """Converts a list of strings to a CSV"""
    with io.StringIO() as output:
        writer = csv.writer(output)
        writer.writerows(strings)
        return output.getvalue()


def prompt_auto_and(s: str, max_length: int) -> str:
    # This regex will match words, sequences within quotes, parentheses with numbers, and parentheses followed by a series of plus (+) or minus (-) signs
    pattern_quotes = r'"[^"]*"'
    pattern_parentheses_number = r"\([^)]*\)\d*\.?\d*"
    pattern_parentheses_plus_minus = r"\([^)]*\)[+-]+"
    pattern_parentheses = r"\([^)]*\)"
    pattern_word = r"\S+"

    # Compile all patterns into a single regex pattern
    pattern = re.compile(
        "|".join(
            [
                pattern_parentheses_plus_minus,
                pattern_parentheses_number,
                pattern_parentheses,
                pattern_quotes,
                pattern_word,
            ]
        )
    )

    words: list[str] = pattern.findall(s)

    chunks: list[str] = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word)
        chunk_length = len(current_chunk)
        # If adding the new word exceeds the max_length, start a new chunk unless we have an empty chunk
        if current_length + word_length + (chunk_length > 0) > max_length and chunk_length > 0:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length + (chunk_length > 1)

    # Add the last chunk to the result if it's not empty
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # handle 1 or 0 chunks
    if len(chunks) < 2:
        return "" if not chunks else chunks[0]

    # Escape double quotes in each chunk
    escaped_chunks = [chunk.replace('"', '\\"') for chunk in chunks]
    # Format the chunks as a single string in the specified format
    formatted_chunks = ",".join(f'"{chunk}"' for chunk in escaped_chunks)
    return f"({formatted_chunks}).and()"


@invocation_output("prompt_to_file_output")
class PromptsToFileInvocationOutput(BaseInvocationOutput):
    """Base class for invocation that writes to a file and returns nothing of use"""


@invocation(
    "prompt_to_file",
    title="Prompts To File",
    tags=["prompt", "file"],
    category="prompt",
    version="1.0.1",
)
class PromptsToFileInvocation(BaseInvocation):
    """Save prompts to a text file"""

    file_path: str = InputField(
        description="Path to prompt text file",
    )
    prompts: Union[str, list[str]] = InputField(
        description="Prompt or collection of prompts to write",
        input=Input.Connection,
    )
    append: bool = InputField(
        default=True,
        description="Append or overwrite file",
    )

    def invoke(self, context: InvocationContext) -> PromptsToFileInvocationOutput:
        with open(self.file_path, "a" if self.append else "w", encoding="utf-8") as f:
            if isinstance(self.prompts, list):
                for line in self.prompts:
                    f.write(line + "\n")
            else:
                f.write((self.prompts or "") + "\n")

        return PromptsToFileInvocationOutput()


class PTFields(BaseModel):
    """Prompt Tools Fields for an image generated in InvokeAI."""

    positive_prompt: Optional[str]
    positive_style_prompt: Optional[str]
    negative_prompt: Optional[str]
    negative_style_prompt: Optional[str]
    seed: Optional[int]
    width: Optional[int]
    height: Optional[int]
    steps: Optional[int]
    cfg_scale: Optional[float]
    denoising_start: Optional[float]
    denoising_end: Optional[float]
    scheduler: SCHEDULER_NAME_VALUES


@invocation_output("pt_fields_collect_output")
class PTFieldsCollectOutput(BaseInvocationOutput):
    """PTFieldsCollect Output"""

    pt_fields: str = OutputField(description="PTFields in Json Format")


@invocation(
    "pt_fields_collect",
    title="PTFields Collect",
    tags=["prompt", "fields"],
    category="prompt",
    version="1.0.1",
)
class PTFieldsCollectInvocation(BaseInvocation):
    """Collect Prompt Tools Fields for an image generated in InvokeAI."""

    positive_prompt: Optional[str] = InputField(
        description="The positive prompt parameter",
    )
    positive_style_prompt: Optional[str] = InputField(
        description="The positive style prompt parameter",
    )
    negative_prompt: Optional[str] = InputField(
        description="The negative prompt parameter",
    )
    negative_style_prompt: Optional[str] = InputField(
        description="The negative prompt parameter",
    )
    seed: Optional[int] = InputField(
        description=FieldDescriptions.seed,
    )
    width: Optional[int] = InputField(
        description=FieldDescriptions.width,
    )
    height: Optional[int] = InputField(
        description=FieldDescriptions.height,
    )
    steps: Optional[int] = InputField(
        description=FieldDescriptions.steps,
    )
    cfg_scale: Optional[float] = InputField(
        description=FieldDescriptions.cfg_scale,
    )
    denoising_start: Optional[float] = InputField(
        description=FieldDescriptions.denoising_start,
    )
    denoising_end: Optional[float] = InputField(
        description=FieldDescriptions.denoising_end,
    )
    scheduler: Optional[SCHEDULER_NAME_VALUES] = InputField(
        description=FieldDescriptions.scheduler,
    )

    def invoke(self, context: InvocationContext) -> PTFieldsCollectOutput:
        x: str = str(
            json.dumps(
                PTFields(
                    positive_prompt=self.positive_prompt,
                    positive_style_prompt=self.positive_style_prompt,
                    negative_prompt=self.negative_prompt,
                    negative_style_prompt=self.negative_style_prompt,
                    seed=self.seed,
                    width=self.width,
                    height=self.height,
                    steps=self.steps,
                    cfg_scale=self.cfg_scale,
                    denoising_start=self.denoising_start,
                    denoising_end=self.denoising_end,
                    scheduler=self.scheduler,
                ).model_dump()
            )
        )
        return PTFieldsCollectOutput(pt_fields=x)


@invocation_output("pt_fields_expand_output")
class PTFieldsExpandOutput(BaseInvocationOutput):
    """Expand Prompt Tools Fields for an image generated in InvokeAI."""

    positive_prompt: str = OutputField(
        description="The positive prompt",
    )
    positive_style_prompt: str = OutputField(
        description="The positive style prompt",
    )
    negative_prompt: str = OutputField(
        description="The negative prompt",
    )
    negative_style_prompt: str = OutputField(
        description="The negative prompt",
    )
    seed: int = OutputField(
        description=FieldDescriptions.seed,
    )
    width: int = OutputField(
        description=FieldDescriptions.width,
    )
    height: int = OutputField(
        description=FieldDescriptions.height,
    )
    steps: int = OutputField(
        description=FieldDescriptions.steps,
    )
    cfg_scale: float = OutputField(
        description=FieldDescriptions.cfg_scale,
    )
    denoising_start: float = OutputField(
        description=FieldDescriptions.denoising_start,
    )
    denoising_end: float = OutputField(
        description=FieldDescriptions.denoising_end,
    )
    scheduler: SCHEDULER_NAME_VALUES = OutputField(
        description=FieldDescriptions.scheduler,
    )


@invocation(
    "pt_fields_expand",
    title="PTFields Expand",
    tags=["prompt", "fields"],
    category="prompt",
    version="1.0.0",
)
class PTFieldsExpandInvocation(BaseInvocation):
    """Save Expand PTFields into individual items"""

    pt_fields: str = InputField(
        description="PTFields in json Format",
    )

    def invoke(self, context: InvocationContext) -> PTFieldsExpandOutput:
        fields = json.loads(self.pt_fields)

        return PTFieldsExpandOutput(
            positive_prompt=fields.get("positive_prompt"),
            positive_style_prompt=fields.get("positive_style_prompt"),
            negative_prompt=fields.get("negative_prompt"),
            negative_style_prompt=fields.get("negative_style_prompt"),
            seed=fields.get("seed"),
            width=fields.get("width"),
            height=fields.get("height"),
            steps=fields.get("steps"),
            cfg_scale=fields.get("cfg_scale"),
            denoising_start=fields.get("denoising_start"),
            denoising_end=fields.get("denoising_end"),
            scheduler=fields.get("scheduler"),
        )


@invocation_output("prompt_strength_collection_output")
class PromptStrengthOutput(BaseInvocationOutput):
    """Base class for nodes that output a collection of images"""

    collection: list[str] = OutputField(
        description="Prompt strength collection",
    )

    value: str = OutputField(
        description="Prompt strength",
    )


@invocation(
    "prompt_strength",
    title="Prompt Strength",
    tags=["prompt"],
    category="prompt",
    version="1.1.0",
)
class PromptStrengthInvocation(BaseInvocation):
    """Takes a prompt string and float strength and outputs a new string in the format of (prompt)strength"""

    collection: list[str] = InputField(
        default=[],
        description="Collection of Prompt strengths",
    )

    prompt: str = InputField(
        default="",
        description="Prompt to work on",
        ui_component=UIComponent.Textarea,
    )
    strength: float = InputField(default=1, gt=0, description="strength of the prompt")

    def invoke(self, context: InvocationContext) -> PromptStrengthOutput:
        prompt_strength: str = f"({self.prompt}){self.strength}"
        self.collection.append(prompt_strength)
        return PromptStrengthOutput(value=prompt_strength, collection=self.collection)


COMBINE_TYPE = Literal[".and", ".blend"]


@invocation(
    "prompt_strengths_combine",
    title="Prompt Strengths Combine",
    tags=["prompt", "combine"],
    category="prompt",
    version="1.0.1",
)
class PromptStrengthsCombineInvocation(BaseInvocation):
    """Takes a collection of prompt strength strings and converts it into a combined .and() or .blend() structure. Blank prompts are ignored"""

    prompt_strengths: list[str] = InputField(
        default=[""],
        description="Prompt strengths to combine",
    )
    combine_type: COMBINE_TYPE = InputField(
        default=".and",
        description="Combine type .and() or .blend()",
    )

    def invoke(self, context: InvocationContext) -> StringOutput:
        strings: list[str] = []
        numbers: list[float] = []
        for item in self.prompt_strengths:
            string, number = item.rsplit(")", 1)
            string = string[1:].strip()
            number = float(number)
            if len(string) > 0:
                strings.append(f'"{string}"')
                numbers.append(number)
        return StringOutput(value=f"({','.join(strings)}){self.combine_type}({','.join(map(str, numbers))})")


@invocation(
    "csv_to_index_string",
    title="CSV To Index String",
    tags=["random", "string", "csv"],
    category="util",
    version="1.1.0",
    use_cache=False,
)
class CSVToIndexStringInvocation(BaseInvocation):
    """CSVToIndexString converts a CSV to a String at index with a random option"""

    csv_string: str = InputField(
        default="",
        description="csv string",
        ui_component=UIComponent.Textarea,
    )
    random: bool = InputField(
        default=True,
        description="Random Index?",
    )
    index: int = InputField(
        default=0,
        description="zero based index into CSV array (note index will wrap around if out of bounds)",
    )

    def invoke(self, context: InvocationContext) -> StringOutput:
        strings = csv_line_to_list(self.csv_string)
        if self.random:
            output = random.choice(strings)
        else:
            output = strings[self.index % len(strings)]
        return StringOutput(value=output)


@invocation(
    "strings_to_csv",
    title="Strings To CSV",
    tags=["string", "csv"],
    category="util",
    version="1.0.0",
    use_cache=False,
)
class StringsToCSVInvocation(BaseInvocation):
    """Strings To CSV converts a a list of Strings into a CSV"""

    strings: Union[str, list[str]] = InputField(
        default="",
        description="String or Collection of Strings to convert to CSV format",
        ui_component=UIComponent.Textarea,
    )

    def invoke(self, context: InvocationContext) -> StringOutput:
        output = list_to_csv(self.strings if isinstance(self.strings, list) else [self.strings])
        return StringOutput(value=output)


@invocation(
    "prompt_auto_and",
    title="Prompt Auto .and()",
    tags=["prompt", "and"],
    category="prompt",
    version="1.0.0",
)
class PromptAutoAndInvocation(BaseInvocation):
    """Takes a prompt string then chunks it up into a .and() output if over the max length"""

    prompt: str = InputField(
        default="",
        description="Prompt to auto .and()",
        ui_component=UIComponent.Textarea,
    )
    max_length: int = InputField(default=200, gt=1, description="Maximum chunk length in characters")

    def invoke(self, context: InvocationContext) -> StringOutput:
        return StringOutput(value=prompt_auto_and(self.prompt, self.max_length))
