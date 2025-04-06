from autogen import register_function
import embeddings
#from embeddings import vectorstore
import memory
from typing import Annotated
import user_proxy
#import hr_conv
import hr_retr
import it_retr
#import groupchatmanager


"""@hr_retr.hr_retrieval.register_for_llm(
    name="retrieve_context", description="Retrieves relevant context from the HR vector database based on a query."
)
#@user_proxy.user_proxy.register_for_execution(name="retrieve_context")
@groupchatmanager.group_chat_manager.register_for_execution(name="retrieve_context")"""


"""@hr_retr.hr_retrieval.register_for_llm(
    name="retrieve_context",
    description="Retrieves relevant HR context based on a query."
)
@hr_retr.hr_retrieval.register_for_execution(name="retrieve_context")"""

def retrieve_context(search_instruction: Annotated[str, "search instruction"]) -> str:

    """Given an instruction on what knowledge you need to find, search the user's documents for information particular to them, their projects, and their domain.
    This is simple document search, it cannot perform any other complex tasks.
    This will not give you any results from the internet. Do not assume it can retrieve the latest news pertaining to any subject."""
    
    results = embeddings.vectorstore.similarity_search(search_instruction, k=3)  # Get top 3 relevant chunks

    if results:
        #return " ".join([result.page_content for result in results])  # Return the most relevant chunks
        context = " ".join([result.page_content for result in results])
        memory.log_message('tool', context)
        print(context)
        return context + "\n\n Terminate"
    return "Policy not found. Please refine your query."

hr_retr.hr_retrieval.register_for_execution(name="retrieve_context")(retrieve_context)
it_retr.it_retrieval.register_for_execution(name="retrieve_context")(retrieve_context)
user_proxy.user_proxy.register_for_execution(name="retrieve_context")(retrieve_context) #add user proxy

"""register_function(
    tools.retrieve_context,
    caller=hr_conv.hr_conversational,    # The agent that suggests the tool call
    executor=hr_retr.hr_retrieval,  # The agent that actually executes the function
    description="Retrieves relevant context from the HR vector database based on a query",
)"""

"""d_retrieve_context = hr_retr.hr_retrieval.register_for_llm(
        description="retrieve content for code generation and question answering.", api_style="function"
    )(retrieve_context)

hr_retr.hr_retrieval.register_for_execution()(d_retrieve_context)"""


