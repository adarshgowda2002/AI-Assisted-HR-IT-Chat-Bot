import autogen
import hr_conv
import hr_retr
import it_conv
import it_retr
import user_proxy
import router
import tools

def custom_speaker_selection_method(last_speaker, group_chat):
    last_message = group_chat.messages[-1] if group_chat.messages else None
    if last_message:
        last_agent_name = last_message.get('name', '')
        if last_agent_name == user_proxy.user_proxy.name:
            return router.router  # After user_proxy, route to router
        elif last_agent_name == router.router.name:
            # Decide whether to hand off to HR or IT conversational agent based on router's output
            content = last_message.get('content', "")
            if "HR" in content:
                return hr_conv.hr_conversational
            elif "IT" in content:
                return it_conv.it_conversational
        elif last_agent_name == hr_conv.hr_conversational.name:
            if "retrieve_context" in last_message.get('content', ""):
                return hr_retr.hr_retrieval
        elif last_agent_name == it_conv.it_conversational.name:
            if "retrieve_context" in last_message.get('content', ""):
                return it_retr.it_retrieval
        elif last_agent_name == hr_retr.hr_retrieval.name:
            return hr_conv.hr_conversational
        elif last_agent_name == it_retr.it_retrieval.name:
            return it_conv.it_conversational
    # Default to user_proxy if no specific handoff condition is met
    return user_proxy.user_proxy


group_chat = autogen.GroupChat(
    agents=[user_proxy.user_proxy, router.router, hr_conv.hr_conversational, it_conv.it_conversational, hr_retr.hr_retrieval, it_retr.it_retrieval],
    speaker_selection_method=custom_speaker_selection_method,
    messages=[]
)

group_chat_manager = autogen.GroupChatManager(
    name="group_chat_manager",
    groupchat=group_chat,
    system_message="You manage conversations.",
)
