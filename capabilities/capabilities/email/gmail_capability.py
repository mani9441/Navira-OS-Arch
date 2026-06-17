# capabilities/gmail_capability.py
import base64
from typing import Dict, Any
from email.mime.text import MIMEText
from capabilities.capability import Capability

class GmailCapability(Capability):
    def __init__(self):
        self.name = "gmail_suite"
        self.description = "Accesses mailbox frameworks to query email history feeds, load single communications, or dispatch new outbound emails."
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address string."},
                "subject": {"type": "string", "description": "The subject line text of the email."},
                "body": {"type": "string", "description": "The main content body string of the email."},
                "msg_id": {"type": "string", "description": "The unique ID string of a targeted message to fetch."},
                "query": {"type": "string", "description": "Search keyword phrase for filtering threads."}
            }
        }
        
        self.internal_tools = {
            "list_messages": {
                "description": "Search user mailboxes, check recent threads, or filter recent history by a specific keyword phrase.",
                "required_fields": []  # Contextual queries are fully optional
            },
            "get_message": {
                "description": "Retrieve the full content details, subject, sender, and snippet of a specific single message via an ID.",
                "required_fields": ["msg_id"]
            },
            "send_email": {
                "description": "Compose and securely dispatch a brand new outbound email message directly to a recipient destination address.",
                "required_fields": ["to", "subject", "body"]
            }
        }

    async def execute(self, context: Any, sub_tool: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if sub_tool == "list_messages":
            query_filter = inputs.get("query", "")
            return {
                "status": "success",
                "filter_used": query_filter if query_filter else "None (Global Feed)",
                "messages": [
                    {"id": "msg_f101", "from": "alerts@github.com", "subject": "Build Succeeded"},
                    {"id": "msg_f202", "from": "nanna@family.com", "subject": "Re: Project updates"}
                ]
            }
            
        elif sub_tool == "get_message":
            msg_id = inputs.get("msg_id")
            return {
                "status": "success",
                "message_details": {
                    "id": msg_id,
                    "from": "alerts@github.com",
                    "subject": "Build Succeeded",
                    "body": "Your integration build for navira-os-arch passed all downstream validation checks cleanly."
                }
            }
            
        elif sub_tool == "send_email":
            to = inputs.get("to")
            subject = inputs.get("subject")
            body = inputs.get("body")
            
            # Underlying base64 structural compilation representation
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            raw_payload = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            print(f"[KERNEL EXECUTION] Dispatched urlsafe base64 email payload to {to}. Length: {len(raw_payload)}")
            return {
                "status": "success",
                "message_id": "sent_v1_mock_id",
                "recipient": to
            }
            
        return {"status": "error", "message": f"Unknown internal tool path: '{sub_tool}'"}