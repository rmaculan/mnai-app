from rest_framework import serializers
from .models import Conversation, Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'message', 'response', 'created_at', 'is_function_call', 
                 'function_name', 'function_args', 'function_result']

class ConversationSerializer(serializers.ModelSerializer):
    chats = ChatSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'user', 'provider', 'created_at', 
                 'updated_at', 'is_active', 'is_archived', 'is_pinned',
                 'is_favorite', 'tags', 'shared_with', 'deleted_at', 'chats']
        read_only_fields = ['user', 'created_at', 'updated_at', 'is_active']
        
    def create(self, validated_data):
        # Set the current user as the conversation owner
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
