from autogen import AssistantAgent
import config

def create_agent(name, system_message, temperature):
    llm_config = {
        "config_list": config.config_list,
        "temperature": temperature
    }
    return AssistantAgent(
        name=name,
        llm_config=llm_config,
        system_message=system_message,
        is_termination_msg=lambda msg: "Terminate" in msg["content"]
    )

# Routing agent (temperature 0)
router = create_agent(
    name="Router",
    system_message="""You are a Routing Agent. Analyze user queries and determine whether they should be handled by HR or IT. 
Respond EXACTLY with either 'HR' or 'IT'. Do not include any other text in your response.""",
    temperature=0
)