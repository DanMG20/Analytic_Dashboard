    # -*- coding: utf-8 -*-

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from tabulate import tabulate
SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']

API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = 'credenciales/credenciales_google.json'
def get_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_local_server()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def execute_api_request(client_library_function, **kwargs):
  response = client_library_function(
    **kwargs
  ).execute()
  return response


if __name__ == '__main__':
  # Disable OAuthlib's HTTPs verification when running locally.
  # *DO NOT* leave this option enabled when running in production.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  youtubeAnalytics = get_service()
  resultado = execute_api_request(
      youtubeAnalytics.reports().query,
      ids='channel==MINE',
      startDate='2025-08-01',
      endDate='2025-08-29',
      metrics='views,estimatedMinutesWatched,subscribersGained,cardImpressions,cardTeaserClickRate',
      dimensions='video'
  )

  headers =['video','views','likes','subscribersGained','estimatedMinutesWatched','cardImpressions','cardTeaserClickRate']
  
  tabla = tabulate(resultado['rows'], headers = headers,tablefmt= "pretty")
  print(tabla)

  with open("tabla.txt", "w") as file:
    file.write(tabla)

