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
    if esconfig['queries'][i]['name'] in ['error_log_agps_server_device_download_100']:
        esconfig['queries'][i]['name'] = Gauge(esconfig['queries'][i]['name'], esconfig['queries'][i]['description'], ['instance', 'log_file_path', 'device_imei'], registry=registry)
    elif esconfig['queries'][i]['name'] in ['error_log_agps_filesync_download_vendor_files', 'error_log_agps_server_sync_files']:
        esconfig['queries'][i]['name'] = Gauge(esconfig['queries'][i]['name'], esconfig['queries'][i]['description'], ['instance', 'log_file_path', 'vendor'], registry=registry)
    else:
        esconfig['queries'][i]['name'] = Gauge(esconfig['queries'][i]['name'], esconfig['queries'][i]['description'], ['instance', 'log_file_path'], registry=registry)

@app.route('/metrics')
def hello():
    resultlist=[]
    for i in range(len(esconfig['queries'])):
        error_log_keyword = esconfig['queries'][i]['error_log_keyword']
        field_t3 = ""
        if str(esconfig['queries'][i]['name']) in ['gauge:error_log_agps_server_device_download_100']:
            field_t3 = "error_log.device_imei"
        if str(esconfig['queries'][i]['name']) in ['gauge:error_log_agps_filesync_download_vendor_files', 'gauge:error_log_agps_server_sync_files']:
            field_t3 = "error_log.vendor"
        es_req = executequery(es_host, es_port, es_index, error_log_keyword, field_t3=field_t3)
        result = []
        result.append(esconfig['queries'][i]['name'])
        for res in es_req:
            result.append(res)
        resultlist.append(result)

    try:
        for i in range(len(esconfig['queries'])):
            if str(esconfig['queries'][i]['name']) in ["gauge:error_log_agps_server_device_download_100"]:
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0], log_file_path=resultlist[i][j][1], device_imei=str(resultlist[i][j][2])).set(str(resultlist[i][j][3]))
            elif str(esconfig['queries'][i]['name']) in ['gauge:error_log_agps_filesync_download_vendor_files', 'gauge:error_log_agps_server_sync_files']:
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0], log_file_path=resultlist[i][j][1], vendor=str(resultlist[i][j][2])).set(str(resultlist[i][j][3]))
            else:
                for j in range(1, len(resultlist[i])):
                    esconfig['queries'][i]['name'].labels(instance=resultlist[i][j][0], log_file_path=resultlist[i][j][1]).set(resultlist[i][j][2])

        return Response(generate_latest(registry), mimetype='text/plain')
    finally:
        for i in range(len(esconfig['queries'])):
            esconfig['queries'][i]['name'].clear()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9096)
