from elasticsearch import Elasticsearch

def executequery(es_host,es_port,es_index,error_log_keyword,aggs_field_t1="agent.hostname",aggs_field_t2=""):
    es = Elasticsearch(
        [f'{es_host}:{es_port}'],
        # 在做任何操作之前，先进行嗅探
        # sniff_on_start=True,
        # # 节点没有响应时，进行刷新，重新连接
        sniff_on_connection_fail=True,
        # # 每 60 秒刷新一次
        sniffer_timeout=60
    )

    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "error_log.keyword": error_log_keyword
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-1m",
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "group_t1": {
                "terms": {
                    "field": aggs_field_t1
                },
                "aggs": {
                    "group_t2": {
                        "terms": {
                            "field": aggs_field_t2
                        }
                    }
                }
            }
        },
        "size": 0
    }

    result = es.search(index=es_index,body=query_body)
    result = result['aggregations']['group_t1']['buckets']
    reallist=[]
    for i in range(len(result)):
        if not result[i]['group_t2']['buckets']:
            tmplist=[]
            tmplist.append(result[i]['key'])
            tmplist.append(result[i]['doc_count'])
            reallist.append(tmplist)
        else:
            for j in range(len(result[i]['group_t2']['buckets'])):
                tmplist = []
                tmplist.append(result[i]['key'])
                tmplist.append(result[i]['group_t2']['buckets'][j]['key'])
                tmplist.append(result[i]['group_t2']['buckets'][j]['doc_count'])
                reallist.append(tmplist)

    return reallist