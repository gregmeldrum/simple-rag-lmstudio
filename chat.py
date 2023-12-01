from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import prompt
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import textwrap
import gradio
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma
import os

os.environ["TOKENIZERS_PARALLELISM"] = "true"
os.environ["OPENAI_API_KEY"] = "dummy-key"


# TODO: Callbacks support token-wise streaming
#callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# Verbose is required to pass to the callback manager

temperature = 0.1 # Use a value between 0 and 2. Lower = factual, higher = creative
n_gpu_layers = 43  # Change this value based on your model and your GPU VRAM pool.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

# Make sure the model path is correct for your system!
llm = OpenAI(
       openai_api_base='http://localhost:1234/v1',
       openai_api_key='dummy-key'
       )

#llm = LlamaCpp(
#    model_path="./models/zephyr-7b-alpha.Q6_K.gguf",
#    temperature=temperature,
#    max_tokens=256,
#    n_ctx=4096,
#    top_p=0.95,
#    n_gpu_layers=n_gpu_layers,
#    n_batch=n_batch,
#    #callback_manager=callback_manager,
#    verbose=True,
#)

## Follow the default prompt style from the OpenOrca-Platypus2 huggingface model card.

def get_prompt():
  return """<|system|>Use the following Context information to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer.</s>
<|user|>Context: {context}
User Question: {question}</s>
<|assistant|>
"""

def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split('\n')

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = '\n'.join(wrapped_lines)

    return wrapped_text

def process_llm_response(llm_response):
    if not llm_response:
      return "Please enter a question"
    print(wrap_text_preserve_newlines(llm_response['result']))
    print('\n\nSources:')
    for source in llm_response["source_documents"]:
        print(source.metadata['source'])
    response = llm_response['result']
    response = response.split("### Response")[0]
    return response

def startChat():

   embedding_directory = "./content/chroma_db"
   embedding_model=HuggingFaceBgeEmbeddings(model_name='BAAI/bge-base-en', model_kwargs={'device':'cpu'})
   embedding_db = Chroma(persist_directory=embedding_directory, embedding_function=embedding_model)

   prompt_template = get_prompt()

   llama_prompt = PromptTemplate(
       template=prompt_template, input_variables=["context", "question"]
   )

   chain_type_kwargs = {"prompt": llama_prompt}


   retriever = embedding_db.as_retriever(search_type="mmr", search_kwargs={'k': 5})

   # create the chain to answer questions
   qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type="stuff",
                                       retriever=retriever,
                                       chain_type_kwargs=chain_type_kwargs,
                                       return_source_documents=True)

   def runChain(query, history):
     return process_llm_response(qa_chain(query))

   app = gradio.ChatInterface(runChain)
   app.queue()
   app.launch(share=False, debug=True)
