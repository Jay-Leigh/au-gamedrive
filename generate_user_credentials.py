"""
Generates a refresh token for use with both the Google Ads API and the
Data Manager API. Run this once, follow the printed URL, then copy the
refresh token it prints into your .env as GOOGLE_ADS_REFRESH_TOKEN.

Usage:
    python generate_user_credentials.py -c path\\to\\client_secret.json
"""

import argparse
from google_auth_oauthlib.flow import InstalledAppFlow

_SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/datamanager",
]


def main(client_secrets_path: str):
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes=_SCOPES)
    credentials = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
    )

    print("\nAccess token:", credentials.token)
    print("\nRefresh token:", credentials.refresh_token)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a refresh token with adwords + datamanager scopes.")
    parser.add_argument(
        "-c", "--client_secrets_path",
        required=True,
        help="Path to the client_secret_....json file downloaded from Google Cloud Console.",
    )
    args = parser.parse_args()
    main(args.client_secrets_path)