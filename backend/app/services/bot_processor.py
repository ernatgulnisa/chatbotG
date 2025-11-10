"""
Bot Message Processor
Processes incoming messages through bot scenarios
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.conversation import Message, Conversation
from app.models.customer import Customer
from app.models.bot import Bot, BotScenario
from app.services.whatsapp import WhatsAppService, get_whatsapp_service


class BotProcessor:
    """Process messages through bot scenarios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_message(self, message: Message) -> bool:
        """
        Process incoming message through bot logic
        
        Args:
            message: Incoming message object
            
        Returns:
            True if processed by bot, False otherwise
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == message.conversation_id
            ).first()
            
            if not conversation:
                return False
            
            # Check if conversation is assigned to a bot
            if not conversation.assigned_bot_id:
                # Try to find active bot for this business
                bot = self.db.query(Bot).filter(
                    Bot.business_id == conversation.business_id,
                    Bot.is_active == True,
                    Bot.whatsapp_number_id == conversation.whatsapp_number_id
                ).first()
                
                if bot:
                    conversation.assigned_bot_id = bot.id
                    self.db.commit()
                else:
                    # No bot available, human takeover
                    return False
            
            bot = self.db.query(Bot).filter(
                Bot.id == conversation.assigned_bot_id
            ).first()
            
            if not bot or not bot.is_active:
                return False
            
            # Get WhatsApp service
            whatsapp_service = await get_whatsapp_service(
                conversation.whatsapp_number_id,
                self.db
            )
            
            if not whatsapp_service:
                return False
            
            # First, try to match keyword scenarios
            matched_scenario = await self._match_keyword_scenario(bot, message)
            
            if matched_scenario:
                # Send response from matched scenario
                await self._send_scenario_response(
                    conversation,
                    message,
                    matched_scenario,
                    whatsapp_service
                )
                return True
            
            # If no keyword match, check for flow-based scenario
            flow_scenario = self.db.query(BotScenario).filter(
                BotScenario.bot_id == bot.id,
                BotScenario.is_active == True,
                BotScenario.trigger_type == "flow"
            ).order_by(BotScenario.version.desc()).first()
            
            if flow_scenario:
                await self._execute_scenario(
                    conversation,
                    message,
                    flow_scenario,
                    whatsapp_service
                )
                return True
            
            # No scenario matched, send default response
            if bot.default_response:
                await whatsapp_service.send_text_message(
                    to=conversation.customer.phone_number,
                    text=bot.default_response
                )
                self._save_bot_message(conversation, bot.default_response, "text")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing message through bot: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _match_keyword_scenario(
        self,
        bot: Bot,
        message: Message
    ) -> Optional[BotScenario]:
        """
        Match message content against keyword scenarios
        
        Returns:
            Matched BotScenario or None
        """
        import json
        
        # Get all active keyword scenarios
        scenarios = self.db.query(BotScenario).filter(
            BotScenario.bot_id == bot.id,
            BotScenario.is_active == True,
            BotScenario.trigger_type == "keyword"
        ).order_by(BotScenario.priority.asc()).all()
        
        if not scenarios:
            return None
        
        message_text = message.content.lower().strip()
        
        # Try to match each scenario
        for scenario in scenarios:
            try:
                keywords = json.loads(scenario.trigger_value)
                
                for keyword in keywords:
                    keyword_lower = keyword.lower().strip()
                    
                    # Check if keyword is in message
                    if keyword_lower in message_text or message_text in keyword_lower:
                        return scenario
                    
                    # Check exact match for numbers
                    if message_text == keyword_lower:
                        return scenario
                        
            except Exception as e:
                print(f"Error parsing scenario keywords: {e}")
                continue
        
        return None
    
    async def _send_scenario_response(
        self,
        conversation: Conversation,
        incoming_message: Message,
        scenario: BotScenario,
        whatsapp_service: WhatsAppService
    ):
        """Send response from matched scenario"""
        try:
            response_text = scenario.response_message
            
            if response_text:
                await whatsapp_service.send_text_message(
                    to=conversation.customer.phone_number,
                    text=response_text
                )
                
                # Save bot response
                self._save_bot_message(conversation, response_text, "text")
                
        except Exception as e:
            print(f"Error sending scenario response: {e}")
            import traceback
            traceback.print_exc()
    
    async def _execute_scenario(
        self,
        conversation: Conversation,
        incoming_message: Message,
        scenario: BotScenario,
        whatsapp_service: WhatsAppService
    ):
        """
        Execute bot scenario based on flow data
        
        Args:
            conversation: Current conversation
            incoming_message: User's message
            scenario: Bot scenario with flow_data
            whatsapp_service: WhatsApp service instance
        """
        flow_data = scenario.flow_data
        
        if not flow_data or not flow_data.get("nodes"):
            return
        
        # Get current position in flow (stored in conversation metadata)
        current_node_id = conversation.bot_state.get("current_node_id") if conversation.bot_state else None
        
        nodes = {node["id"]: node for node in flow_data.get("nodes", [])}
        edges = flow_data.get("edges", [])
        
        # If no current node, start from welcome node
        if not current_node_id:
            welcome_nodes = [n for n in nodes.values() if n.get("type") == "welcome"]
            if welcome_nodes:
                current_node = welcome_nodes[0]
                await self._execute_node(
                    current_node,
                    conversation,
                    incoming_message,
                    whatsapp_service,
                    nodes,
                    edges
                )
            return
        
        # Process from current node
        current_node = nodes.get(current_node_id)
        if current_node:
            await self._process_user_response(
                current_node,
                conversation,
                incoming_message,
                whatsapp_service,
                nodes,
                edges
            )
    
    async def _execute_node(
        self,
        node: Dict[str, Any],
        conversation: Conversation,
        incoming_message: Message,
        whatsapp_service: WhatsAppService,
        nodes: Dict[str, Any],
        edges: List[Dict[str, Any]]
    ):
        """Execute a single node in the flow"""
        node_type = node.get("type")
        node_data = node.get("data", {})
        customer = conversation.customer
        
        # Update current position
        if not conversation.bot_state:
            conversation.bot_state = {}
        conversation.bot_state["current_node_id"] = node.get("id")
        self.db.commit()
        
        # Execute based on node type
        if node_type in ["welcome", "message"]:
            # Send text message
            text = node_data.get("message", "")
            if text:
                await whatsapp_service.send_text_message(
                    to=customer.phone_number,
                    text=text
                )
                
                # Save bot response
                self._save_bot_message(conversation, text, "text")
                
                # Move to next node automatically
                await self._move_to_next_node(
                    node,
                    conversation,
                    incoming_message,
                    whatsapp_service,
                    nodes,
                    edges
                )
        
        elif node_type == "question":
            # Send question and wait for response
            question = node_data.get("question", "")
            if question:
                await whatsapp_service.send_text_message(
                    to=customer.phone_number,
                    text=question
                )
                self._save_bot_message(conversation, question, "text")
                # Don't move to next node - wait for user response
        
        elif node_type == "buttons":
            # Send interactive buttons
            message_text = node_data.get("message", "")
            buttons = node_data.get("buttons", [])
            
            if message_text and buttons:
                button_list = [
                    {"id": str(i), "title": btn.get("label", f"Option {i}")}
                    for i, btn in enumerate(buttons[:3])  # Max 3 buttons
                ]
                
                await whatsapp_service.send_interactive_buttons(
                    to=customer.phone_number,
                    body_text=message_text,
                    buttons=button_list
                )
                self._save_bot_message(conversation, message_text, "interactive")
                # Wait for button click
        
        elif node_type == "condition":
            # Evaluate condition and branch
            condition_type = node_data.get("conditionType", "contains")
            condition_value = node_data.get("value", "")
            user_input = incoming_message.content.lower()
            
            result = self._evaluate_condition(
                condition_type,
                condition_value,
                user_input
            )
            
            # Find appropriate edge based on condition result
            await self._branch_on_condition(
                node,
                result,
                conversation,
                incoming_message,
                whatsapp_service,
                nodes,
                edges
            )
        
        elif node_type == "action":
            # Perform action (save to CRM, create deal, etc.)
            action_type = node_data.get("actionType", "save_to_crm")
            
            if action_type == "save_to_crm":
                # Save conversation data to customer
                field = node_data.get("field", "")
                value = incoming_message.content
                
                if field and value:
                    if not customer.custom_fields:
                        customer.custom_fields = {}
                    customer.custom_fields[field] = value
                    self.db.commit()
            
            elif action_type == "create_deal":
                # Create a deal
                from app.models.deal import Deal
                deal = Deal(
                    business_id=conversation.business_id,
                    customer_id=customer.id,
                    title=f"Deal from {customer.name}",
                    stage="new",
                    amount=0
                )
                self.db.add(deal)
                self.db.commit()
            
            elif action_type == "assign_tag":
                # Assign tag to customer
                tag = node_data.get("tag", "")
                if tag:
                    if not customer.tags:
                        customer.tags = []
                    if tag not in customer.tags:
                        customer.tags.append(tag)
                    self.db.commit()
            
            elif action_type == "human_takeover":
                # Transfer to human agent
                conversation.is_bot_active = False
                conversation.assigned_agent_id = None  # Can assign to specific agent
                self.db.commit()
                
                await whatsapp_service.send_text_message(
                    to=customer.phone_number,
                    text="Соединяю вас с оператором..."
                )
                return
            
            # Move to next node after action
            await self._move_to_next_node(
                node,
                conversation,
                incoming_message,
                whatsapp_service,
                nodes,
                edges
            )
    
    async def _process_user_response(
        self,
        current_node: Dict[str, Any],
        conversation: Conversation,
        incoming_message: Message,
        whatsapp_service: WhatsAppService,
        nodes: Dict[str, Any],
        edges: List[Dict[str, Any]]
    ):
        """Process user's response to current node"""
        node_type = current_node.get("type")
        
        if node_type == "question":
            # Save answer and move to next
            field = current_node.get("data", {}).get("saveAs", "")
            if field:
                customer = conversation.customer
                if not customer.custom_fields:
                    customer.custom_fields = {}
                customer.custom_fields[field] = incoming_message.content
                self.db.commit()
            
            await self._move_to_next_node(
                current_node,
                conversation,
                incoming_message,
                whatsapp_service,
                nodes,
                edges
            )
        
        elif node_type == "buttons":
            # User clicked button or sent text
            # Move to corresponding next node
            await self._move_to_next_node(
                current_node,
                conversation,
                incoming_message,
                whatsapp_service,
                nodes,
                edges
            )
        
        elif node_type == "condition":
            # Re-evaluate condition with new message
            await self._execute_node(
                current_node,
                conversation,
                incoming_message,
                whatsapp_service,
                nodes,
                edges
            )
    
    async def _move_to_next_node(
        self,
        current_node: Dict[str, Any],
        conversation: Conversation,
        incoming_message: Message,
        whatsapp_service: WhatsAppService,
        nodes: Dict[str, Any],
        edges: List[Dict[str, Any]]
    ):
        """Find and execute next node in flow"""
        current_id = current_node.get("id")
        
        # Find outgoing edge
        next_edge = next(
            (e for e in edges if e.get("source") == current_id),
            None
        )
        
        if next_edge:
            next_node_id = next_edge.get("target")
            next_node = nodes.get(next_node_id)
            
            if next_node:
                await self._execute_node(
                    next_node,
                    conversation,
                    incoming_message,
                    whatsapp_service,
                    nodes,
                    edges
                )
        else:
            # End of flow
            conversation.bot_state["current_node_id"] = None
            conversation.is_bot_active = False
            self.db.commit()
    
    async def _branch_on_condition(
        self,
        condition_node: Dict[str, Any],
        condition_result: bool,
        conversation: Conversation,
        incoming_message: Message,
        whatsapp_service: WhatsAppService,
        nodes: Dict[str, Any],
        edges: List[Dict[str, Any]]
    ):
        """Branch to next node based on condition result"""
        current_id = condition_node.get("id")
        
        # Find edge with matching label
        target_label = "true" if condition_result else "false"
        next_edge = next(
            (e for e in edges 
             if e.get("source") == current_id 
             and e.get("label", "").lower() == target_label),
            None
        )
        
        # If no labeled edge, take first available
        if not next_edge:
            next_edge = next(
                (e for e in edges if e.get("source") == current_id),
                None
            )
        
        if next_edge:
            next_node_id = next_edge.get("target")
            next_node = nodes.get(next_node_id)
            
            if next_node:
                await self._execute_node(
                    next_node,
                    conversation,
                    incoming_message,
                    whatsapp_service,
                    nodes,
                    edges
                )
    
    def _evaluate_condition(
        self,
        condition_type: str,
        condition_value: str,
        user_input: str
    ) -> bool:
        """Evaluate condition against user input"""
        user_input = user_input.lower().strip()
        condition_value = condition_value.lower().strip()
        
        if condition_type == "contains":
            return condition_value in user_input
        elif condition_type == "equals":
            return user_input == condition_value
        elif condition_type == "starts_with":
            return user_input.startswith(condition_value)
        elif condition_type == "ends_with":
            return user_input.endswith(condition_value)
        elif condition_type == "regex":
            import re
            try:
                return bool(re.search(condition_value, user_input))
            except:
                return False
        else:
            return False
    
    def _save_bot_message(
        self,
        conversation: Conversation,
        content: str,
        message_type: str
    ):
        """Save bot's outgoing message to database"""
        bot_message = Message(
            conversation_id=conversation.id,
            direction="outbound",
            content=content,
            message_type=message_type,
            status="sent",
            timestamp=datetime.utcnow()
        )
        self.db.add(bot_message)
        self.db.commit()
