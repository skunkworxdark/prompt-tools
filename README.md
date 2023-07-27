# Prompt-tools-nodes
A set of InvokeAI nodes that add general prompt manipulation tools.

Currently contains 4 nodes:- PromptJoin, PromptReplace, PromptSpiltNeg and PromptsToFile

1. PromptJoin - Joins to prompts into one.
2. PromptReplace - performs a search and replace on a prompt. With the option of using regex.
3. PromptSplitNeg - splits a prompt into positive and negative using the old V2 method of [] for negative.
4. PromptToFile - saves a prompt or collection of prompts to a file. one per line. There is an append/overwrite option.

If you want to use this node py file place it in the folder .venv\Lib\site-packages\invokeai\app\invocations. Note: if these nodes get added to main then the py file will need to be removed from this folder to prevent a clash. 
