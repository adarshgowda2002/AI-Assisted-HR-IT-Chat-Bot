from autogen import AssistantAgent
from autogen import AfterWorkOption, OnCondition, register_hand_off
import config
import tools
#import hr_retr
#import embeddings
#import memory


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
        function_map={"retrieve_context": tools.retrieve_context}
    )
    

HR_CONV_PROMPT = """You are an AI HR assistant.
    When you receive a message, figure out a solution and provide a final answer. The message will be accompanied with contextual information. Use the contextual information to help you provide a solution.
    Make sure to provide a thorough answer that directly addresses the message you received.
    The context may contain extraneous information that does not apply to your instruction. If so, just extract whatever is useful or relevant and use it to complete your instruction.
    When the context does not include enough information to complete the task, use your available tools to retrieve the specific information you need.
    When you are using knowledge tools to complete the instruction, answer the instruction only using the results from the search; do no supplement with your own knowledge.
    Be persistent in finding the information you need before giving up.
    If the task is able to be accomplished without using tools, then do not make any tool calls.
    When you have accomplished the instruction posed to you, you will reply with the text: ##SUMMARY## - followed with an answer.
    Important: If you are unable to accomplish the task, whether it's because you could not retrieve sufficient data, or any other reason, reply only with ##TERMINATE##.

    # Tool Use
    You have access to the retrieve_context tool. Only use these available tools and do not attempt to use anything not listed - this will cause an error.
    Respond in the format: <function_call> {"name": retrieve_context, "search_instruction": the search query}. Do not use variables. Use this format EXACTLY.
    Only call one tool at a time.
    When suggesting tool calls, please respond with a JSON for a function call with its proper arguments that best answers the given prompt.
    """
    
hr_conversational = create_agent(
    name="HR_Conversational",
    system_message=HR_CONV_PROMPT,
    temperature=0.3
)

