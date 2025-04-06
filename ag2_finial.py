from autogen import ConversableAgent, GroupChat, GroupChatManager
import embeddings
from typing import List, Tuple, Dict
import config
import tools
from hr_conv import create_agent as create_hr_agent, HR_CONV_PROMPT
from it_conv import create_agent as create_it_agent, IT_CONV_PROMPT

class ContextSwitchDetector:
    def __init__(self):
        self.embeddings = embeddings.embeddings
        self.hr_keywords = [
            "leave", "benefits", "payroll", "hr", "policy", "vacation", 
            "onboarding", "salary", "employee", "contract", "hiring"
        ]
        self.it_keywords = [
            "password", "access", "computer", "system", "email", "software",
            "network", "printer", "login", "technical", "error"
        ]

    def detect_context(self, message: str) -> Tuple[str, float]:
        """
        Detects whether a message is HR or IT related
        Returns: tuple of (context_type, confidence_score)
        """
        message = message.lower()
        
        hr_count = sum(1 for keyword in self.hr_keywords if keyword in message)
        it_count = sum(1 for keyword in self.it_keywords if keyword in message)
        
        total = hr_count + it_count
        if total == 0:
            return "UNKNOWN", 0.0
            
        hr_score = hr_count / total
        it_score = it_count / total
        
        if hr_score > it_score:
            return "HR", hr_score
        else:
            return "IT", it_score

def create_agents():
    """Create and configure all necessary agents"""
    # Create HR and IT agents with different temperatures
    hr_agent = create_hr_agent(
        name="hr_agent",
        system_message=HR_CONV_PROMPT,
        temperature=0.7
    )
    
    it_agent = create_it_agent(
        name="it_agent",
        system_message=IT_CONV_PROMPT,
        temperature=0.7
    )
    
    # Create router agent to handle context switching
    router_config = {
        "config_list": config.config_list,
        "temperature": 0.2  # Lower temperature for more consistent routing
    }
    
    router = ConversableAgent(
        name="router",
        system_message="""You are a routing agent that determines whether queries should be handled by HR or IT.
        Analyze the query content and route to the appropriate department.
        If a query involves both HR and IT, coordinate between both departments.""",
        llm_config=router_config
    )
    
    return hr_agent, it_agent, router

def setup_group_chat():
    """Set up the group chat with all agents"""
    hr_agent, it_agent, router = create_agents()
    context_detector = ContextSwitchDetector()
    
    def smart_speaker_selection(last_speaker: ConversableAgent, 
                              group_chat: GroupChat) -> ConversableAgent:
        """Smart speaker selection based on context detection"""
        if not group_chat.messages:
            return router
            
        last_message = group_chat.messages[-1]["content"]
        context, confidence = context_detector.detect_context(last_message)
        
        if context == "HR":
            return hr_agent
        elif context == "IT":
            return it_agent
        else:
            return router
    
    # Create group chat with all agents
    group_chat = GroupChat(
        agents=[hr_agent, it_agent, router],
        messages=[],
        max_round=10,
        speaker_selection_method=smart_speaker_selection
    )
    
    # Create manager to orchestrate the group chat
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config={"config_list": config.config_list}
    )
    
    return manager, group_chat

def handle_query(query: str) -> str:
    """
    Main function to handle incoming queries
    Returns the appropriate response after agent collaboration
    """
    manager, _ = setup_group_chat()
    
    # Initialize chat with the query
    response = manager.initiate_chat(
        message=query,
        sender=manager.groupchat.agents[0]
    )
    
    return response.summary if hasattr(response, 'summary') else str(response)

# Function to register tools/functions for agents
def register_agent_functions():
    """Register available tools/functions for agents to use"""
    function_map = {
        "retrieve_context": tools.retrieve_context,
        # Add other functions as needed
    }
    
    return function_map