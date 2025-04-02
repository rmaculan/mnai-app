#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from chatbot.models import Chat, Conversation
from django.db.models import Q
from django.utils import timezone

def migrate_chats():
    # Get all chats that don't have a conversation
    orphaned_chats = Chat.objects.filter(Q(conversation__isnull=True))
    
    # Group by user
    users_with_orphaned_chats = User.objects.filter(chat__in=orphaned_chats).distinct()
    
    print(f"Found {orphaned_chats.count()} chats without conversations from {users_with_orphaned_chats.count()} users")
    
    # For each user, create a default conversation and assign all their orphaned chats to it
    for user in users_with_orphaned_chats:
        # Create a default conversation for the user with all required fields
        conversation = Conversation.objects.create(
            user=user,
            title="Imported Conversation",
            provider="openai",  # Required field
            is_active=True,     # Required field
            is_archived=False,  # Required field
            is_favorite=False,  # Required field
            is_pinned=False,    # Required field
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Get all orphaned chats for this user
        user_orphaned_chats = orphaned_chats.filter(user=user)
        
        # Update them to belong to the new conversation
        user_orphaned_chats.update(conversation=conversation)
        
        print(f"Migrated {user_orphaned_chats.count()} chats for user {user.username} to conversation '{conversation.title}'")
    
    # Verify no chats are left without a conversation
    remaining_orphans = Chat.objects.filter(Q(conversation__isnull=True))
    if remaining_orphans.exists():
        print(f"WARNING: {remaining_orphans.count()} chats still don't have a conversation assigned")
    else:
        print("All chats have been successfully migrated to conversations")

if __name__ == "__main__":
    migrate_chats()
