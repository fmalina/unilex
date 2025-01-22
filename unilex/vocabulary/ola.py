"""
OpenAI language assistant
~~~~~~~~~~~~~~~~~~~~~~~~~

Ola finds concepts from controlled vocabularies in documents and tags these documents
with semantic concepts. Ola helps you to process your data and turn it into knowledge.

Ola listens to your story (or reads your document).
Ola than deconstructs the story to concepts matching concepts
already known (in the repository). Creating Tags to points in your story.

Ola reconstructs your story and is able to use synonyms and may even replay your document
in a foreign language if the repository vocabularies are any good.

Ola will learn with you and will take what you give her and turn it into knowledge
that you can export.

If the associations to concepts are wrong you can correct them and improve
quality of your knowledge as well as teach Ola.

Ola lives a life of her own and cares for health of her models.
Don't use output from other "intelligent" systems to feed Ola's input, ever.
Don't give her bullshit either or you'll get cut off.
"""

import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

prompt_tpl = """Write a taxonomy for WATCHES in markdown nested unordered list with
concept names and descriptions separated by ::"""


def taxonomy_prompt(concept):
    return prompt_tpl.replace('WATCHES', concept.capitalize())


def submit_prompt(prompt):
    print(f'>>> {prompt}')
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': prompt}]
    )
    return response.choices[0]['message']['content']


# print(submit_prompt(prompt_tpl))
# print(submit_prompt(taxonomy_prompt('AI')))
# print(submit_prompt(taxonomy_prompt('Animals')))
