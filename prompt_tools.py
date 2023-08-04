from os.path import exists
from typing import Literal, Union, Optional, List
import numpy as np
import re
import json

from pydantic import BaseModel, Field, validator

from .baseinvocation import BaseInvocation, InvocationContext, InvocationConfig
from .prompt import PromptOutput, BaseInvocationOutput


class PromptPosNegOutput(BaseInvocationOutput):
    """Base class for invocations that output a posirtive and negative prompt"""

    # fmt: off
    type: Literal["prompt_pos_neg_output"] = "prompt_pos_neg_output"

    positive_prompt: str = Field(description="The positive prompt")
    negative_prompt: str = Field(description="The negative prompt")
    # fmt: on

    class Config:
        schema_extra = {"required": ["type", "positive_prompt", "negative_prompt"]}

class PromptsToFileInvocationOutput(BaseInvocationOutput):
    """Base class for invocation that writes to a file and returns nothing of use"""
    #fmt: off
    type: Literal["prompts_to_file_output"] = "prompts_to_file_output"
    #fmt: on

    class Config:
        schema_extra = {
            'required': [
                'type'
            ]
        }

class PromptSplitNegInvocation(BaseInvocation):
    """Splits prompt into two prompts, inside [] goes into negative prompt everthing else goes into positive prompt. Each [ and ] character is replaced with a space"""

    type: Literal["prompt_split_neg"] = "prompt_split_neg"
    prompt: str = Field(default='', description="Prompt to split")

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Prompt Spilt Negative",
                "tags": ["prompt", "split", "negative"]
            },
        }

    def invoke(self, context: InvocationContext) -> PromptPosNegOutput:
        p_prompt = ""
        n_prompt = ""
        brackets_depth = 0
        escaped = False

        for char in (self.prompt or ''):
            if char == "[" and not escaped:
                n_prompt += ' '
                brackets_depth += 1 
            elif char == "]" and not escaped:
                brackets_depth -= 1 
                char = ' ' 
            elif brackets_depth > 0:
                n_prompt += char
            else:
                p_prompt += char            

            #keep track of the escape char but only if it isn't escaped already
            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False

        return PromptPosNegOutput(positive_prompt=p_prompt, negative_prompt=n_prompt)


class PromptJoinInvocation(BaseInvocation):
    """Joins prompt a to prompt b"""

    type: Literal["prompt_join"] = "prompt_join"
    prompt_a: str = Field(default='', description="Prompt a - (Left)")
    prompt_b: str = Field(default='', description="Prompt b - (Right)")

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Prompt Join",
                "tags": ["prompt", "join"]
            },
        }

    def invoke(self, context: InvocationContext) -> PromptOutput:
        return PromptOutput(prompt=((self.prompt_a or '') + (self.prompt_b or '')))  

class PromptJoinThreeInvocation(BaseInvocation):
    """Joins prompt a to prompt b to prompt c"""

    type: Literal["prompt_join_three"] = "prompt_join_three"
    prompt_a: str = Field(default='', description="Prompt a - (Left)")
    prompt_b: str = Field(default='', description="Prompt b - (Middle)")
    prompt_c: str = Field(default='', description="Prompt c - (Right)")

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Prompt Join Three",
                "tags": ["prompt", "join"]
            },
        }

    def invoke(self, context: InvocationContext) -> PromptOutput:
        return PromptOutput(prompt=((self.prompt_a or '') + (self.prompt_b or '') + (self.prompt_c or '')))  


class PromptReplaceInvocation(BaseInvocation):
    """Replaces the search string with the replace string in the prompt"""

    type: Literal["prompt_replace"] = "prompt_replace"
    prompt: str = Field(default='', description="Prompt to work on")
    search_string : str = Field(default='', description="String to search for")
    replace_string : str = Field(default='', description="String to replace the search")
    use_regex: bool = Field(default=False, description="Use search string as a regex expression (non regex is case insensitive)")

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Prompt Replace",
                "tags": ["prompt", "replace", "regex"]
            },
        }

    def invoke(self, context: InvocationContext) -> PromptOutput:
        pattern = (self.search_string or '')
        new_prompt = (self.prompt or '')
        if len(pattern) > 0: 
            if not self.use_regex:
                #None regex so make case insensitve 
                pattern = "(?i)" + re.escape(pattern)
            new_prompt = re.sub(pattern, (self.replace_string or ''), new_prompt)
        return PromptOutput(prompt=new_prompt)  

class PromptsToFileInvocation(BaseInvocation):
    '''Save prompts to a text file'''
    # fmt: off
    type: Literal['prompt_to_file'] = 'prompt_to_file'

    # Inputs
    file_path: str = Field(description="Path to prompt text file")
    prompts: Union[str, list[str], None] = Field(default=None, description="Prompt or collection of prompts to write")
    append: bool = Field(default=True, description="Append or overwrite file")
    #fmt: on

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Prompts To File",
                "tags": ["prompt", "file"],
                "type_hints": {
                    "prompts": "string",
                }
            },
        }
        
    def invoke(self, context: InvocationContext) -> PromptsToFileInvocationOutput:
        if self.append:
            file_mode = 'a'
        else:
            file_mode = 'w'

        with open(self.file_path, file_mode) as f:
            if isinstance(self.prompts, list):
                for line in (self.prompts):
                    f.write ( line + '\n' )
            else:
                f.write((self.prompts or '') + '\n')
 
        return PromptsToFileInvocationOutput()

class PTFields(BaseModel):
    """Prompt Tools Fields for an image generated in InvokeAI."""
    positive_prompt: str = Field(default='', description="The positive prompt parameter")
    positive_style_prompt: str = Field(default='', description="The positive style prompt parameter")
    negative_prompt: str = Field(default='', description="The negative prompt parameter")
    negative_style_prompt: str = Field(default='', description="The negative prompt parameter")
    width: int = Field(default=512, description="The width parameter")
    height: int = Field(default=512, description="The height parameter")
    seed: int = Field(default=0, description="The seed used for noise generation")
    steps: int = Field(default=10, description="The number of steps used for inference")
    cfg_scale: float = Field(default=7.0, description="The classifier-free guidance scale parameter")

class PTFieldsCollectOutput(BaseInvocationOutput):
    """PTFieldsCollect Output"""
    type: Literal["pt_fields_collect_output"] = "pt_fields_collect_output"

    pt_fields: str = Field(description="PTFields in Json Format")

class PTFieldsCollectInvocation(BaseInvocation):
    """Prompt Tools Fields for an image generated in InvokeAI."""
    type: Literal["pt_fields_collect"] = "pt_fields_collect"

    positive_prompt: str = Field(default='', description="The positive prompt parameter")
    positive_style_prompt: str = Field(default='', description="The positive style prompt parameter")
    negative_prompt: str = Field(default='', description="The negative prompt parameter")
    negative_style_prompt: str = Field(default='', description="The negative prompt parameter")
    width: int = Field(default=512, description="The width parameter")
    height: int = Field(default=512, description="The height parameter")
    seed: int = Field(default=0, description="The seed used for noise generation")
    steps: int = Field(default=10, description="The number of steps used for inference")
    cfg_scale: float = Field(default=7.0, description="The classifier-free guidance scale parameter")

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "PTFields Collect",
                "tags": ["prompt", "file"],
            },
        }
       
    def invoke(self, context: InvocationContext) -> PTFieldsCollectOutput:
        x:str = str(json.dumps(
                    PTFields(
                        positive_prompt = self.positive_prompt, 
                        positive_style_prompt = self.positive_style_prompt,
                        negative_prompt = self.negative_prompt,
                        negative_style_prompt = self.negative_style_prompt,
                        width = self.width,
                        height = self.height,
                        seed = self.seed,
                        steps = self.steps,
                        cfg_scale = self.cfg_scale,
                ).dict()
            )
        )
        return PTFieldsCollectOutput(pt_fields=x)


class PTFieldsExpandOutput(BaseInvocationOutput):
    """Prompt Tools Fields for an image generated in InvokeAI."""
    type: Literal["pt_fields_expand_output"] = "pt_fields_expand_output"    

    positive_prompt: str = Field(description="The positive prompt parameter")
    positive_style_prompt: str = Field(description="The positive style prompt parameter")
    negative_prompt: str = Field(description="The negative prompt parameter")
    negative_style_prompt: str = Field(description="The negative prompt parameter")
    width: int = Field(description="The width parameter")
    height: int = Field(description="The height parameter")
    seed: int = Field(description="The seed used for noise generation")
    steps: int = Field(description="The number of steps used for inference")
    cfg_scale: float = Field(description="The classifier-free guidance scale parameter")

    class Config:
        schema_extra = {
            'required': ['type'],
            "ui": {
                "type_hints": {
                    },
                },
            }
        
class PTFieldsExpandInvocation(BaseInvocation):
    '''Save Expand PTFields into individual items'''
    type: Literal['pt_fields_expand'] = 'pt_fields_expand'
    pt_fields: str = Field(default=None, description="PTFields in Json Format")

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "PTFields Expand",
                "tags": ["prompt", "file"],
                "type_hints": {
                    "pt_fields": "string",
                }
            },
        }
       
    def invoke(self, context: InvocationContext) -> PTFieldsExpandOutput:
        fields = json.loads(self.pt_fields)

        return PTFieldsExpandOutput(
            positive_prompt = fields.get('positive_prompt'),
            positive_style_prompt = fields.get('positive_style_prompt'),
            negative_prompt = fields.get('negative_prompt'),
            negative_style_prompt = fields.get('negative_style_prompt'),
            width = fields.get('width'),
            height = fields.get('height'),
            seed = fields.get('seed'),
            steps = fields.get('steps'),
            cfg_scale = fields.get('cfg_scale'),
        )

