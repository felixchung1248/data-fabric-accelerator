from flask import Flask, request, jsonify
import requests
import logging
import os
from requests.auth import HTTPBasicAuth
import json
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig
from datahub.specific.dataset import DatasetPatchBuilder


app = Flask(__name__)
datahub_url = os.environ['DATA_CATALOG_URL']

# Function to retrieve value by key
def get_value_by_key(data, search_key):
    for item in data:
        if item['key'] == search_key:
            return item['value']
    return None  # Return None if the key is not found

@app.after_request
def after_request(response):
    # Only add CORS headers if the Origin header exists and is from localhost
    origin = request.headers.get('Origin')
    if origin and 'localhost' in origin:
        # Add CORS headers to the response
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/listalldatacatalogdatasets', methods=['GET'])
def ListAllDataCatalogDatasets():
    final_list = []
    query = """
                {
                  search(input: { type: DATASET, query: "*", start: 0, count: 9999 }) {
                    start
                    count
                    total
                    searchResults {
                      entity {
                         urn
                         type
                         ...on Dataset {
                            name
                         }
                      }
                    }
                  }
                }
            """
    headers = {
                'Content-Type': 'application/json'
            }
    
    payload = {
        'query': query
    }

    graphqlUrl = f"{datahub_url}/api/graphql"
    response = requests.post(graphqlUrl, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_json = response.json()
        view_list = response_json['data']['search']['searchResults']
        for item in view_list:
            dataset_name = item['entity']['name']
            query = f"""
                {{
                  dataset(urn: "{item['entity']['urn']}") {{
                  properties {{
                    description
                    ,customProperties{{
                         key,value
                    }}
                  }}
                  schemaMetadata{{
                      fields{{
                          fieldPath
                          ,description
                          ,type
                          ,tags {{
                            tags {{
                              tag {{
                                name
                                urn
                                  properties {{
                                    description
                                    colorHex
                                  }}
                              }}
                            }}
                          }}
                      }}
                  }}
                    ownership 
                    {{
                      owners 
                      {{
                        owner 
                        {{
                          ... on CorpUser 
                          {{
                            urn
                            type
                          }}
                          ... on CorpGroup 
                          {{
                            urn
                            type
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
            """
            payload = {
                'query': query
            }
            response = requests.post(graphqlUrl, headers=headers, data=json.dumps(payload))
            response_json = response.json()
            data = response_json['data']
            dataset = data['dataset']
            ownership = dataset['ownership']
            owners = ownership['owners']
            table_description = dataset['properties']['description']
            rating = get_value_by_key(dataset['properties']['customProperties'],'rating')
            rating = rating if float(rating) > -1 else 'No rating'
            fields = dataset['schemaMetadata']
            
            for field in fields['fields']:
              if field['tags'] is not None and any(item['tag']['name'] == 'sensitive' for item in field['tags']['tags']):
                field['isSensitive'] = "True"
              else:
                field['isSensitive'] = "False"
                
            for owner in owners:
                user_urn = owner['owner']['urn']
                response = requests.get(f"{datahub_url}/entities/{user_urn}", headers=headers)
                response_json = response.json()
                owner_aspects = response_json['value']['com.linkedin.metadata.snapshot.CorpUserSnapshot']['aspects']

                for item in owner_aspects:
                    if "com.linkedin.identity.CorpUserEditableInfo" in item:
                        user_info = item["com.linkedin.identity.CorpUserEditableInfo"]
                        owner_name = user_info.get("displayName", "Name not found")
                        break
                    else:
                        owner_name = "Name not found"
                owner['owner_name'] = owner_name
            info = {"dataset_name": dataset_name, "owners": owners, "table_description": table_description, "rating": rating, "fields":fields}
            final_list.append(info)
         
        return jsonify(final_list)   
    else:
        print(f"Failed to get metadata for dataset: {response.content}")
        return "Error occurred", 400


@app.route('/rate-dataset', methods=['POST'])
def rate_dataset():
    logging.info("rate_dataset() function processed a request.")
    result = {}
    try:
        rating = float(request.args.get("rating"))
        dataset_name = request.args.get("dataset_name")
        client = DataHubGraph(DatahubClientConfig(server=datahub_url))
        urns = client.get_urns_by_filter(entity_types=["dataset"], query=dataset_name)
        urn = next(urns)
        current_rating = float(client.get_dataset_properties(urn).customProperties["rating"])
        if current_rating == -1:
            rating_count = 1
        else:
            rating = (current_rating + rating)/2
            rating_count = int(client.get_dataset_properties(urn).customProperties["rating_count"]) + 1
            
        for patch_mcp in (
                DatasetPatchBuilder(urn).set_custom_properties({
                "rating": str(rating),
                "rating_count": str(rating_count)
            }).build()
        ):
            client.emit(patch_mcp)
            result["code"] = 200
            result["message"] = "Success"
            result["rating"] = rating
    except Exception as e:
        logging.exception(f"Error: {e}")
        result["code"] = 400
        result["message"] = f"Error: {e}"
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7011)

    
