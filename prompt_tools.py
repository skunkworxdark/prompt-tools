from os.path import exists
from typing import Literal, Union, Optional, List
import numpy as np
import re
from pydantic import Field, validator

from .baseinvocation import BaseInvocation, InvocationContext, InvocationConfig
from .prompt import PromptCollectionOutput, PromptOutput, BaseInvocationOutput

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


