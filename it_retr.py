from autogen import ConversableAgent, AssistantAgent
import config
#import tools
#import hr_conv

IT_RETR_PROMPT = """

You are the IT Retrieval Agent. Your role is to fetch accurate IT-related information by executing the 'retrieve_context' tool whenever a retrieval is needed. Follow these guidelines strictly:

1. When prompted with a IT query, immediately call the 'retrieve_context' function using the provided query parameters.
2. After executing the tool, encapsulate the raw retrieval output between <RETRIEVED></RETRIEVED> tags.
3. Do not generate any additional information—only use the data returned by the tool.

Your responses must strictly adhere to these rules. Format your output exactly as specified.

"""

def create_agent(name, system_message, temperature):
    llm_config = {
        "config_list": config.config_list,
        "temperature": temperature
    }
    return AssistantAgent(
        name=name,
        llm_config=llm_config,
        system_message=system_message,
        is_termination_msg=lambda msg: "Terminate" in msg["content"],
        #function_map={"retrieve_context": tools.retrieve_context}
    )



it_retrieval = create_agent(
    name="IT_Retrieval",
    system_message=IT_RETR_PROMPT,
    temperature=0,
)
