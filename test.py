import autogen
from typing import Annotated
import config
import embeddings    # Ensure your vectorstore is set up here
import memory        # For logging tool outputs
import tools         # We'll register our tool function here

# ---------------------------------------------------------------------------
# Define the tool function for HR retrieval.
# ---------------------------------------------------------------------------
def retrieve_context(search_instruction: Annotated[str, "search instruction"]) -> str:
    """
    Given an instruction on what knowledge to retrieve, search the user's documents.
    This function performs a simple document search using a vector database.
    It returns the most relevant chunks of information.
    """
    results = embeddings.vectorstore.similarity_search(search_instruction, k=3)  # Top 3 results
    if results:
        context = "\n".join([result.page_content for result in results])
        memory.log_message('tool', context)
        print("Tool output:", context)
        return f"<RETRIEVED>\n{context}\n</RETRIEVED>"
    return "<RETRIEVED>Policy not found. Please refine your query.</RETRIEVED>"

# ---------------------------------------------------------------------------
# Create the necessary agents
# ---------------------------------------------------------------------------
user_proxy = autogen.UserProxyAgent(name="User_proxy", human_input_mode="ALWAYS", code_execution_config=False)

router = autogen.AssistantAgent(
    name="Router",
    system_message="You are the router. Decide whether to hand off to HR or IT. Reply with a single word: 'HR' or 'IT'.",
    llm_config={"config_list": config.config_list}
)

hr_conversational = autogen.AssistantAgent(
    name="HR_Conversational",
    system_message="You are the HR conversational agent. When a user asks about HR-related topics, **immediately** call `retrieve_context: [query]` without asking for clarification. The query should be a broad category like 'Company Policy', 'Leave Policy', or 'Code of Conduct'. Do **not** ask follow-up questions.",
    llm_config={"config_list": config.config_list}
)


it_conversational = autogen.AssistantAgent(
    name="IT_Conversational",
    system_message="You are the IT conversational agent.",
    llm_config={"config_list": config.config_list}
)

it_retrieval = autogen.AssistantAgent(
    name="IT_Retrieval",
    system_message="You are the IT retrieval agent. Follow similar rules as HR retrieval.",
    llm_config={"config_list": config.config_list},
    is_termination_msg=lambda msg: "Terminate" in msg["content"]
)

# HR Retrieval Agent
hr_retrieval = autogen.AssistantAgent(
    name="HR_Retrieval",
    system_message="""
    You are the HR Retrieval Agent. Your role is to fetch accurate HR-related information by executing the 'retrieve_context' tool.
    Follow these guidelines strictly:
    1. When prompted with an HR query, immediately call the 'retrieve_context' function.
    2. After executing the tool, encapsulate the raw retrieval output between <RETRIEVED></RETRIEVED> tags.
    3. Do not generate any additional information—only use the data returned by the tool.
    """,
    llm_config={"config_list": config.config_list, "temperature": 0},
    function_map={"retrieve_context": retrieve_context},
    is_termination_msg=lambda msg: "Terminate" in msg["content"]
)

# ---------------------------------------------------------------------------
# Custom Speaker Selection for Group Chat
# ---------------------------------------------------------------------------
def custom_speaker_selection_method(last_speaker, group_chat):
    last_message = group_chat.messages[-1] if group_chat.messages else None
    if last_message:
        last_agent_name = last_message.get('name', '')
        if last_agent_name == user_proxy.name:
            return router  # Route to Router after user input.
        elif last_agent_name == router.name:
            if "HR" in last_message.get('content', ""):
                return hr_conversational
            elif "IT" in last_message.get('content', ""):
                return it_conversational
        elif last_agent_name == hr_conversational.name:
            if "retrieve_context" in last_message.get('content', ""):
                return hr_retrieval
        elif last_agent_name == it_conversational.name:
            if "retrieve_context" in last_message.get('content', ""):
                return it_retrieval
        elif last_agent_name == hr_retrieval.name:
            return hr_conversational
        elif last_agent_name == it_retrieval.name:
            return it_conversational
    return user_proxy  # Default fallback

# ---------------------------------------------------------------------------
# Create the Group Chat with All Agents
# ---------------------------------------------------------------------------
group_chat = autogen.GroupChat(
    agents=[
        user_proxy,
        router,
        hr_conversational,
        it_conversational,
        hr_retrieval,
        it_retrieval
    ],
    speaker_selection_method=custom_speaker_selection_method,
    messages=[]
)

group_chat_manager = autogen.GroupChatManager(
    name="group_chat_manager",
    groupchat=group_chat,
    system_message="You manage conversations."
)

# ---------------------------------------------------------------------------
# Initiate the Conversation
# ---------------------------------------------------------------------------
user_query = "tell me about the company policies"
user_proxy.initiate_chat(
    group_chat_manager,
    message=user_query
)