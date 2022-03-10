from es_query import executequery
from read_yaml import ReadYaml
from flask import Flask, Response
from prometheus_client import generate_latest, Gauge, CollectorRegistry

app = Flask(__name__)
registry = CollectorRegistry()
esconfig = ReadYaml().read_conf()
es_host = esconfig['es']['host']
es_port = esconfig['es']['port']
es_index = esconfig['index']

for i in range(len(esconfig['queries'])):
    if esconfig['queries'][i]['name'] == 'error_log_agps_server_device_download_100':
        esconfig['queries'][i]['name'] = Gauge(esconfig['queries'][i]['name'], esconfig['queries'][i]['description'],['instance','device_imei'], registry=registry)
    elif esconfig['queries'][i]['name'] == 'error_log_agps_filesync_download_supply_files' or 'error_log_agps_server_sync_files':
        esconfig['queries'][i]['name'] = Gauge(esconfig['queries'][i]['name'], esconfig['queries'][i]['description'],['instance', 'vendor'], registry=registry)
    else:
        esconfig['queries'][i]['name'] = Gauge(esconfig['queries'][i]['name'], esconfig['queries'][i]['description'],['instance'], registry=registry)

@app.route('/metrics')
def hello():
    resultlist=[]
    for i in range(len(esconfig['queries'])):
        error_log_keyword = esconfig['queries'][i]['error_log_keyword']
        aggs_field_t2 = ""
        if str(esconfig['queries'][i]['name']) == 'gauge:error_log_agps_server_device_download_100':
            aggs_field_t2 = "error_log.device_imei"
        if str(esconfig['queries'][i]['name']) == 'gauge:error_log_agps_filesync_download_vendor_files':
            aggs_field_t2 = "error_log.vendor"
        if str(esconfig['queries'][i]['name']) == 'gauge:error_log_agps_server_sync_files':
            aggs_field_t2 = "error_log.vendor"
        es_req = executequery(es_host, es_port, es_index, error_log_keyword,aggs_field_t2=aggs_field_t2)
        result = []
        result.append(esconfig['queries'][i]['name'])
        for res in es_req:
            result.append(res)
        resultlist.append(result)

    try:
        for i in range(len(esconfig['queries'])):
            print(esconfig['queries'][i]['name'])
            if str(esconfig['queries'][i]['name']) == "gauge:error_log_agps_server_device_download_100":
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0],device_imei=str(resultlist[i][j][1])).set(str(resultlist[i][j][2]))
            elif str(esconfig['queries'][i]['name']) == 'gauge:error_log_agps_filesync_download_vendor_files':
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0],vendor=str(resultlist[i][j][1])).set(str(resultlist[i][j][2]))
            elif str(esconfig['queries'][i]['name']) == 'gauge:error_log_agps_server_sync_files':
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0],vendor=str(resultlist[i][j][1])).set(str(resultlist[i][j][2]))
            else:
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0]).set(str(resultlist[i][j][1]))
        return Response(generate_latest(registry), mimetype='text/plain')
    finally:
        for i in range(len(esconfig['queries'])):
            esconfig['queries'][i]['name'].clear()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9096)
