import uuid
from typing import List, Tuple

import boto3
from opensearchpy import OpenSearch
from opensearchpy import RequestsHttpConnection, AWSV4SignerAuth

from engine.base_client.search import BaseSearcher
from engine.clients.opensearch.config import (
    OPENSEARCH_INDEX, process_connection_params,
)
from engine.clients.opensearch.parser import OpenSearchConditionParser


class ClosableOpenSearch(OpenSearch):
    def __del__(self):
        self.close()


class OpenSearchSearcher(BaseSearcher):
    search_params = {}
    client: OpenSearch = None
    parser = OpenSearchConditionParser()

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        host, port, user, password, aws_secret_access_key, aws_access_key_id, region, service, init_params = process_connection_params(connection_params, host)
        session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        credentials = session.get_credentials()
        auth = AWSV4SignerAuth(credentials, region, service)
        cls.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20
        )
        cls.search_params = search_params['params']

    @classmethod
    def search_one(cls, vector, meta_conditions, top, schema) -> List[Tuple[int, float]]:
        while True:
            try:
                query = {
                    "knn": {
                        "vector": {
                            "vector": vector,
                            "k": top,
                        }
                    }
                }

                meta_conditions = cls.parser.parse(meta_conditions)
                if meta_conditions:
                    query = {
                        "bool": {
                            "must": [query],
                            "filter": meta_conditions,
                        }
                    }
                source_excludes = ['vector']
                if schema is not None:
                    source_excludes.extend(list(schema.keys()))
                res = cls.client.search(
                    index=OPENSEARCH_INDEX,
                    body={
                        "query": query,
                        "size": top,
                    },
                    _source_excludes=source_excludes,
                    params={
                        "timeout": 60,
                    },
                )
                # print(cls.client.indices.get_settings(index="bench"))
                return [
                    (uuid.UUID(hex=hit["_id"]).int, hit["_score"])
                    for hit in res["hits"]["hits"]
                ]
            except Exception as e:
                print(f"🐛 open search exception in search_one, {e}")

    def setup_search(self, host, distance, connection_params: dict, search_params: dict):
        if search_params and search_params['params']:
            self.init_client(host=host,
                             distance=distance,
                             connection_params=connection_params,
                             search_params=search_params)
            self.client.indices.put_settings(
                body=search_params['params'], index=OPENSEARCH_INDEX
            )
