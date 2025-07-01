# # authenticate.py

# import time
# import streamlit as st
# import google_auth_oauthlib.flow
# from googleapiclient.discovery import build
# from token_manager import AuthTokenManager

# class Authenticator:
#     def __init__(
#         self,
#         client_id: str,
#         client_secret: str,
#         token_key: str,
#         redirect_uri: str,
#         cookie_name: str = "auth_jwt",
#         token_duration_days: int = 7,
#     ):
#         st.session_state["connected"] = st.session_state.get("connected", False)
#         self.client_id = client_id
#         self.client_secret = client_secret
#         self.redirect_uri = redirect_uri
#         self.auth_token_manager = AuthTokenManager(
#             cookie_name=cookie_name,
#             token_key=token_key,
#             token_duration_days=token_duration_days,
#         )

#     def _initialize_flow(self):
#         # Create a client_config dictionary instead of reading from a file
#         client_config = {
#             "web": {
#                 "client_id": self.client_id,
#                 "client_secret": self.client_secret,
#                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                 "token_uri": "https://oauth2.googleapis.com/token",
#                 "redirect_uris": [self.redirect_uri],
#             }
#         }
        
#         # Use Flow.from_client_config instead of from_client_secrets_file
#         flow = google_auth_oauthlib.flow.Flow.from_client_config(
#             client_config=client_config,
#             scopes=[
#                 "openid",
#                 "https://www.googleapis.com/auth/userinfo.profile",
#                 "https://www.googleapis.com/auth/userinfo.email",
#             ],
#             redirect_uri=self.redirect_uri,
#         )
#         return flow

#     def get_auth_url(self):
#         flow = self._initialize_flow()
#         auth_url, _ = flow.authorization_url(
#             access_type="offline", include_granted_scopes="true"
#         )
#         return auth_url

#     def login_widget(self):
#         if not st.session_state["connected"]:
#             auth_url = self.get_auth_url()
#             st.link_button("Login with Google", auth_url, use_container_width=True)

#     def check_authentication(self):
#         if st.session_state["connected"]:
#             return

#         token = self.auth_token_manager.get_decoded_token()
#         if token is not None:
#             st.session_state["connected"] = True
#             st.session_state["user_info"] = token
#             st.rerun()

#         auth_code = st.query_params.get("code")
#         if auth_code:
#             st.query_params.clear()
#             try:
#                 flow = self._initialize_flow()
#                 flow.fetch_token(code=auth_code)
#                 creds = flow.credentials

#                 oauth_service = build(serviceName="oauth2", version="v2", credentials=creds)
#                 user_info = oauth_service.userinfo().get().execute()

#                 self.auth_token_manager.set_token(
#                     email=user_info.get("email"),
#                     name=user_info.get("name"),
#                     picture=user_info.get("picture")
#                 )
#                 st.session_state["connected"] = True
#                 st.session_state["user_info"] = user_info
#                 st.rerun()
#             except Exception as e:
#                 st.toast(f":red[Error during authentication: {e}]")

#     def logout(self):
#         st.session_state["connected"] = False
#         st.session_state["user_info"] = None
#         self.auth_token_manager.delete_token()
#         st.success("You have been logged out.")
#         time.sleep(1)
#         st.rerun()
