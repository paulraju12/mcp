"""
Text parser for extracting ticket details from user input.

This module provides functionality to parse natural language and extract
structured ticket information.
"""

import re
import structlog
from typing import Optional, List, Dict, Any
from .categories.ticketing.models.ticket_models import TicketData, TicketType, TicketStatus, TicketPriority

logger = structlog.getLogger(__name__)


async def extract_ticket_details_from_text(user_request: str) -> TicketData:
    """
    Extract ticket details from natural language text.

    Args:
        user_request: The user's natural language request

    Returns:
        TicketData object with extracted information
    """
    logger.info(f"Extracting ticket details from: {user_request}")

    # Initialize default values
    name = "Ticket"
    description = user_request
    ticket_type = TicketType.TASK
    status = TicketStatus.OPEN
    priority = TicketPriority.MEDIUM
    labels = []

    # Extract title/name from the beginning of the request
    title_patterns = [
        r'^create\s+(?:a\s+)?(?:ticket|issue|task)\s+(?:for\s+|about\s+|to\s+)?(.+?)(?:\.|$)',
        r'^(?:i\s+need\s+to\s+|please\s+)?(.+?)(?:\s+ticket|\s+issue|\s+task)?$'
    ]

    for pattern in title_patterns:
        match = re.search(pattern, user_request.lower().strip())
        if match:
            name = match.group(1).strip().title()
            break

    # Extract ticket type
    if any(word in user_request.lower() for word in ['bug', 'error', 'issue', 'problem', 'broken']):
        ticket_type = TicketType.BUG
    elif any(word in user_request.lower() for word in ['feature', 'enhancement', 'improve', 'add']):
        ticket_type = TicketType.FEATURE
    elif any(word in user_request.lower() for word in ['security', 'vulnerability', 'secure']):
        ticket_type = TicketType.SECURITY

    # Extract priority
    if any(word in user_request.lower() for word in ['urgent', 'critical', 'asap', 'immediately']):
        priority = TicketPriority.CRITICAL
    elif any(word in user_request.lower() for word in ['high', 'important', 'priority']):
        priority = TicketPriority.HIGH
    elif any(word in user_request.lower() for word in ['low', 'minor', 'whenever']):
        priority = TicketPriority.LOW

    # Extract labels/tags
    tag_patterns = [
        r'tag(?:ged)?\s+(?:as\s+|with\s+)?([a-zA-Z0-9,\s]+)',
        r'label(?:ed)?\s+(?:as\s+|with\s+)?([a-zA-Z0-9,\s]+)',
        r'categor(?:y|ies)\s+([a-zA-Z0-9,\s]+)'
    ]

    for pattern in tag_patterns:
        match = re.search(pattern, user_request.lower())
        if match:
            tags = [tag.strip() for tag in match.group(1).split(',')]
            labels.extend(tags)

    # Clean up name if it's too generic
    if len(name) < 5 or name.lower() in ['ticket', 'task', 'issue']:
        # Try to extract a more meaningful title
        sentences = user_request.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 10:
                name = first_sentence[:50] + "..." if len(first_sentence) > 50 else first_sentence

    ticket_data = TicketData(
        name=name,
        description=description,
        type=ticket_type,
        status=status,
        priority=priority,
        labels=labels if labels else None
    )

    logger.info(f"Extracted ticket data: {ticket_data.dict()}")
    return ticket_data