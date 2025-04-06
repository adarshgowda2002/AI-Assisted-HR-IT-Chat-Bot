from autogen import UserProxyAgent
#import groupchatmanager

user_proxy = UserProxyAgent(
    name="User_proxy",
    human_input_mode="NEVER",
    code_execution_config=False,
    default_auto_reply="",
    max_consecutive_auto_reply=1,
    is_termination_msg=lambda msg: "##SUMMARY##" in msg["content"]
    or "## Summary" in msg["content"]
    or "##TERMINATE##" in msg["content"]
    or ("tool_calls" not in msg and msg["content"] == ""),

)
