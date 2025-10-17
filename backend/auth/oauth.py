# OAuth Configuration for Social Login
import os
from authlib.integrations.django_client import OAuth
from django.conf import settings

# Initialize OAuth registry
oauth = OAuth()

# Google OAuth Configuration
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Facebook OAuth Configuration
oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
    authorize_url='https://www.facebook.com/v12.0/dialog/oauth',
    access_token_url='https://graph.facebook.com/v12.0/oauth/access_token',
    redirect_uri=os.getenv('FACEBOOK_REDIRECT_URI'),
    client_kwargs={
        'scope': 'email public_profile'
    }
)

class SocialAuthService:
    """Service for handling social authentication"""
    
    @staticmethod
    def get_provider(provider_name):
        """Get OAuth provider by name"""
        return oauth.create_client(provider_name)
    
    @staticmethod
    def handle_callback(provider_name, token):
        """Handle OAuth callback and return user info"""
        client = oauth.create_client(provider_name)
        user_info = client.parse_id_token(token)
        return user_info
