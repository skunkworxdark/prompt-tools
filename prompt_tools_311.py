# 2023 skunkworxdark (https://github.com/skunkworxdark)

import json
import re
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
        ui_order=1,
    )
    prompts: Union[str, list[str]] = InputField(
        description="Prompt or collection of prompts to write",
        ui_order=2,
        input=Input.Connection,
    )
    append: bool = InputField(
        default=True,
        description="Append or overwrite file",
        ui_order=3,
    )

    def invoke(self, context: InvocationContext) -> PromptsToFileInvocationOutput:
        with open(self.file_path, "a" if self.append else "w") as f:
            if isinstance(self.prompts, list):
                for line in self.prompts:
                    f.write(line + "\n")
            else:
                f.write((self.prompts or "") + "\n")

        return PromptsToFileInvocationOutput()


@invocation_output("prompt_pos_neg_output")
class PromptPosNegOutput(BaseInvocationOutput):
    """Base class for invocations that output a positive and negative prompt"""

    positive_prompt: str = OutputField(
        description="Positive prompt",
    )
    negative_prompt: str = OutputField(
        description="Negative prompt",
    )


@invocation(
    "prompt_split_neg",
    title="Prompt Split Negative",
    tags=["prompt", "split", "negative"],
    category="prompt",
    version="1.0.0",
)
class PromptSplitNegInvocation(BaseInvocation):
    """Splits prompt into two prompts, inside [] goes into negative prompt everything else goes into positive prompt. Each [ and ] character is replaced with a space"""

    prompt: str = InputField(
        default="",
        description="Prompt to split",
        ui_component=UIComponent.Textarea,
    )

    def invoke(self, context: InvocationContext) -> PromptPosNegOutput:
        p_prompt = ""
        n_prompt = ""
        brackets_depth = 0
        escaped = False

        for char in self.prompt or "":
            if char == "[" and not escaped:
                n_prompt += " "
                brackets_depth += 1
            elif char == "]" and not escaped:
                brackets_depth -= 1
                char = " "
            elif brackets_depth > 0:
                n_prompt += char
            else:
                p_prompt += char

            # keep track of the escape char but only if it isn't escaped already
            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False

        return PromptPosNegOutput(positive_prompt=p_prompt, negative_prompt=n_prompt)


@invocation(
    "prompt_join",
    title="Prompt Join",
    tags=["prompt", "join"],
    category="prompt",
    version="1.0.0",
)
class PromptJoinInvocation(BaseInvocation):
    """Joins prompt left to prompt right"""

    prompt_left: str = InputField(
        default="",
        description="Prompt Left",
        ui_component=UIComponent.Textarea,
    )
    prompt_right: str = InputField(
        default="",
        description="Prompt Right",
        ui_component=UIComponent.Textarea,
    )

    def invoke(self, context: InvocationContext) -> StringOutput:
        return StringOutput(value=((self.prompt_left or "") + (self.prompt_right or "")))


@invocation(
    "prompt_join_three",
    title="Prompt Join Three",
    tags=["prompt", "join"],
    category="prompt",
    version="1.0.0",
)
class PromptJoinThreeInvocation(BaseInvocation):
    """Joins prompt left to prompt middle to prompt right"""

    prompt_left: str = InputField(default="", description="Prompt Left", ui_component=UIComponent.Textarea)
    prompt_middle: str = InputField(default="", description="Prompt Middle", ui_component=UIComponent.Textarea)
    prompt_right: str = InputField(default="", description="Prompt Right", ui_component=UIComponent.Textarea)

    def invoke(self, context: InvocationContext) -> StringOutput:
        return StringOutput(value=((self.prompt_left or "") + (self.prompt_middle or "") + (self.prompt_right or "")))


@invocation(
    "prompt_replace",
    title="Prompt Replace",
    tags=["prompt", "replace", "regex"],
    category="prompt",
    version="1.0.0",
)
class PromptReplaceInvocation(BaseInvocation):
    """Replaces the search string with the replace string in the prompt"""

    prompt: str = InputField(
        default="",
        description="Prompt to work on",
        ui_component=UIComponent.Textarea,
    )
    search_string: str = InputField(
        default="",
        description="String to search for",
        ui_component=UIComponent.Textarea,
    )
    replace_string: str = InputField(
        default="",
        description="String to replace the search",
        ui_component=UIComponent.Textarea,
    )
    use_regex: bool = InputField(
        default=False,
        description="Use search string as a regex expression (non regex is case insensitive)",
    )

    def invoke(self, context: InvocationContext) -> StringOutput:
        pattern = self.search_string or ""
        new_prompt = self.prompt or ""
        if len(pattern) > 0:
            if not self.use_regex:
                # None regex so make case insensitive
                pattern = "(?i)" + re.escape(pattern)
            new_prompt = re.sub(pattern, (self.replace_string or ""), new_prompt)
        return StringOutput(value=new_prompt)


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
        return StringOutput(value=f'({",".join(strings)}){self.combine_type}({",".join(map(str, numbers))})')
