from elasticsearch import Elasticsearch

def executequery(es_host,es_port,es_index,error_log_keyword,field_t1="agent.hostname",field_t2="log.file.path",field_t3=""):
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
                            "gte": "now-5m",
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "group_t1": {
                "terms": {
                    "field": field_t1
                },
                "aggs": {
                    "group_t2": {
                        "terms": {
                            "field": field_t2
                        },
                        "aggs": {
                            "group_t3": {
                                "terms": {
                                    "field": field_t3
                                }
                            }
                        }
                    }
                }
            }
        },
        "size": 0
    }

    result = es.search(index=es_index,body=query_body)["aggregations"]
    reallist=[]

    for i in range(len(result["group_t1"]["buckets"])):
        for j in range(len(result["group_t1"]["buckets"][i]["group_t2"]["buckets"])):
            if not result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["group_t3"]["buckets"]:
                tmplist = []
                tmplist.append(result["group_t1"]["buckets"][i]["key"])
                tmplist.append(result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["key"])
                tmplist.append(result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["doc_count"])
                reallist.append(tmplist)
            else:
                for k in range(len(result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["group_t3"]["buckets"])):
                    tmplist = []
                    tmplist.append(result["group_t1"]["buckets"][i]["key"])
                    tmplist.append(result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["key"])
                    tmplist.append(result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["group_t3"]["buckets"][k]["key"])
                    tmplist.append(result["group_t1"]["buckets"][i]["group_t2"]["buckets"][j]["group_t3"]["buckets"][k]["doc_count"])
                    reallist.append(tmplist)

    return reallist