# 2023 skunkworxdark (https://github.com/skunkworxdark)

import json
import random
from typing import Literal, Optional, Union

from pydantic import BaseModel

from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    BaseInvocationOutput,
    FieldDescriptions,
    Input,
    InputField,
    InvocationContext,
    OutputField,
    UIComponent,
    UIType,
    invocation,
    invocation_output,
)
from invokeai.app.invocations.latent import SAMPLER_NAME_VALUES
from invokeai.app.invocations.primitives import StringOutput


@invocation_output("prompt_to_file_output")
class PromptsToFileInvocationOutput(BaseInvocationOutput):
    """Base class for invocation that writes to a file and returns nothing of use"""


@invocation(
    "prompt_to_file",
    title="Prompts To File",
    tags=["prompt", "file"],
    category="prompt",
    version="1.0.0",
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
        with open(self.file_path, "a" if self.append else "w") as f:
            if isinstance(self.prompts, list):
                for line in self.prompts:
                    f.write(line + "\n")
            else:
                f.write((self.prompts or "") + "\n")

        return PromptsToFileInvocationOutput()


class PTFields(BaseModel):
    """Prompt Tools Fields for an image generated in InvokeAI."""

    positive_prompt: str
    positive_style_prompt: str
    negative_prompt: str
    negative_style_prompt: str
    seed: int
    width: int
    height: int
    steps: int
    cfg_scale: float
    denoising_start: float
    denoising_end: float
    scheduler: SAMPLER_NAME_VALUES


@invocation_output("pt_fields_collect_output")
class PTFieldsCollectOutput(BaseInvocationOutput):
    """PTFieldsCollect Output"""

    pt_fields: str = OutputField(description="PTFields in Json Format")


@invocation(
    "pt_fields_collect",
    title="PTFields Collect",
    tags=["prompt", "fields"],
    category="prompt",
    version="1.0.0",
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
    scheduler: Optional[SAMPLER_NAME_VALUES] = InputField(
        description=FieldDescriptions.scheduler,
        ui_type=UIType.Scheduler,
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
                ).dict()
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
    scheduler: SAMPLER_NAME_VALUES = OutputField(
        description=FieldDescriptions.scheduler,
        ui_type=UIType.Scheduler,
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
        default=None,
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


@invocation(
    "prompt_strength",
    title="Prompt Strength",
    tags=["prompt"],
    category="prompt",
    version="1.0.0",
)
class PromptStrengthInvocation(BaseInvocation):
    """Takes a prompt string and float strength and outputs a new string in the format of (prompt)strength"""

    prompt: str = InputField(
        default="",
        description="Prompt to work on",
        ui_component=UIComponent.Textarea,
    )
    strength: float = InputField(default=1, gt=0, description="strength of the prompt")

    def invoke(self, context: InvocationContext) -> StringOutput:
        return StringOutput(value=f"({self.prompt}){self.strength}")


COMBINE_TYPE = Literal[".and", ".blend"]


@invocation(
    "prompt_strengths_combine",
    title="Prompt Strengths Combine",
    tags=["prompt", "combine"],
    category="prompt",
    version="1.0.0",
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
        strings = []
        numbers = []
        for item in self.prompt_strengths:
            string, number = item.rsplit(")", 1)
            string = string[1:].strip()
            number = float(number)
            if len(string) > 0:
                strings.append(f'"{string}"')
                numbers.append(number)
        return StringOutput(
            value=f'({",".join(strings)}){self.combine_type}({",".join(map(str, numbers))})'
        )


@invocation(
    "csv_to_index_string",
    title="CSV To Index String",
    tags=["random", "string", "csv"],
    category="util",
    version="1.0.0",
    use_cache=False,
)
class CSVToIndexStringInvocation(BaseInvocation):
    """CSVToIndexString converts a CSV to a String at index with a random option"""

    csv: str = InputField(
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
        strings = self.csv.split(",")
        if self.random:
            output = random.choice(strings)
        else:
            output = strings[self.index % len(strings)]
        return StringOutput(value=output)
