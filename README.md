# Prompt-tools-nodes
A set of InvokeAI nodes that add general prompt manipulation tools.  These where written to accompany the PromptsFromFile node and other prompt generation nodes.

1. PromptJoin - Joins to prompts into one.
2. PromptReplace - performs a search and replace on a prompt. With the option of using regex.
3. PromptSplitNeg - splits a prompt into positive and negative using the old V2 method of [] for negative.
4. PromptToFile - saves a prompt or collection of prompts to a file. one per line. There is an append/overwrite option.
5. PTFieldsCollect - Converts image generation fields into a Json format string that can be passed to Prompt to file. 
6. PTFieldsExpand - Takes Json string and converts it to individual generation parameters This can be fed from the Prompts to file node.
7. PromptJoinThree -  Joins 3 prompt together.

Both of the PTfields nodes should be easy to change to add or remove fields if the ones provided are not correct.


If you want to use this node py file place it in the folder ".venv\Lib\site-packages\invokeai\app\invocations". Note: if these nodes get added to main then the py file will need to be removed from this folder to prevent a clash. 

The main integrated file in my GitHub Repo for this is :- [prompts.py](https://github.com/skunkworxdark/InvokeAI/blob/PromtsFromFile-SupportNodes/invokeai/app/invocations/prompt.py) .

The Pull Request for inclusion in the InvokeAI main is :-  [PR-#3964](https://github.com/invoke-ai/InvokeAI/pull/3964) .

The discord link for discussion is :- [Prompt-Tools](https://discord.com/channels/1020123559063990373/1134084151386058803) .



## PromptNegSplit - details and examples
This would take input in the old 2.3.5 format "Positive [Negative]" and split it into two separate prompts everything inside [] would go to the neg prompt and everything else would go to the positive.  This would allow the PromptsFromFile to contain both positive and negative prompts on a single line. This is the Node name I like the least as it really doesn't split in the normal programming sense its more of an extract but split is an easy concept to get for users.

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/847f0a96-953d-4dc7-b6e2-a7417f106b99)

## PromptJoin - details and example
This would take two prompts and join them into one. The use case I have in mind is that you could add to the beginning or end of individual split prompts.  There are manu more use cases for such a simple node. I thought about calling it PromptConcatenate but feel it is a bit to programming orientated.

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/2a4957c7-e703-444f-b1bd-15c1b91393a7)

## PromptReplace - Details and example
This takes 4 inputs (a prompt, a search string,  a replace string and bool for Regex).  As default the search is case insensitive but there is an option to switch to RegEx for more control on searches.

This can be used to just replace or remove terms from prompts. But due to its simplicity there are many many use cases. but comes into its own with nodes that either generate prompts or load them from other sources.

One such use case I have in mind is the PromptsFromFile would contain multiple template like prompts (e.g "photo of XXXXXX , Nikon", "drawing of XXXXXX in crayon", "Wikihow of XXXXXX, in a cartoo style") with a fixed place holder ( "XXXXXX") that would be replaced for each line of the file with whatever you put tin the replace field. This way you could change the subject of each prompt and try it against multiple templates.

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/3479f673-09c5-4053-a8c9-e9e4ff4bc42e)

## PromptsToFile - details and example
Takes a filepath and a prompt or prompt collection and a bool for append/overwrite toggle.

Filepath:  This is the file that you want to be written to.  if the does not exist it will be created. Please be careful as there is no warning if a file already exists and will be overwritten.

Prompts: This accepts either a single prompt or a collection of prompts as input. 

Append: The defaults to append mode so the new prompts will just be appended to the end of the existing file. if this is disabled a new blank file will be created each time it is called. 

The large node graph below shows how you can use the Collect node make a collection of prompts during an iterate process.  This node graph goes a step further and places the negative inside [] like the old v2 way of doing things but has the benefit of keeping it to one line per prompt.

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/b483a0e9-bd98-44ef-8c0e-0dc1b884deee)
![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/db82f094-ace7-4450-a418-31af64c01724)

## PTFieldsCollect
Converts image generation fields into a Json format string that can be passed to Prompt to file

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/3a716fe3-5e7d-41dd-80a2-3055cb4e7daf)

## PTFieldsExpand
Takes a json string and converts it to individual generation parameters

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/f0d733c1-74f4-4b92-b0c1-a813e7106530)

## PromptJoinThree
Joins 3 prompts together. Useful for surrounding things

![image](https://github.com/skunkworxdark/Prompt-tools-nodes/assets/21961335/d4fa05e1-ef18-44e2-88fd-bbc0ae134e4e)

