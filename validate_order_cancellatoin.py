"""
-> This Atom drops and creates a temp table which contains order ids which are eligbile for cancellation after execution of run_validation_script ssh atom.
"""




#JSON Input


INPUT_TEMPLATE = {
    "data": {
        "flowName": "",
        "company": "",
        "project": "",
        "parameters": [
            {"source_machine": {"entity": ""}}
        ]
    }
}


def handle(json_input):
   

    parameters = extract_parameters(json_input)
    config_details = parameters.get('source_machine')
    print('Using DB Entity: {}'.format(str(config_details)))

    drop_qry = """drop table uf_at_post_cancellation_validation"""    

    crt_qry = """CREATE TABLE uf_at_post_cancellation_validation AS
                    select tbo.order_unit_id , tbo.status from uf_at_cancel_order co , tborder tbo
                    where co.order_id = tbo.order_unit_id"""
    select_query = "select upper(STATUS) ORDER_STATUS from uf_at_post_cancellation_validation"

    output = {}

    try:

        status0, data0 = run_dml_query(config_details, drop_qry, timeout=60000, additional_conn_params={"bypass_validation_ind": True})
        print("data0: "+ str(data0))
        status1, data1 = run_dml_query(config_details, crt_qry, timeout=60000)
        print("data1: "+ str(data1))
        msg = "Query Execution {}"
        print("Query1: {0}\nExecution Status: {1}".format(crt_qry, str(status1)))

        if status1 == constants.get_success():
            print('Table uf_at_post_cancellation_validation created')

            try:
                status2, data2 = run_select_query(config_details, select_query)
                print("Status2: "+status2)
                print("data2: "+ str(data2))

                if status2 == constants.get_success():
                    if data2[0] > 0:
                        output['output'] = str(data2[1][0]["ORDER_STATUS"])
                    else:
                        output['output'] = "No records Found"
                    json_result = success_response(output)
                else:
                    output['reason'] = data2
                    json_result = failure_response(output)
                return json_result

            except Exception as ex:
                output['reason'] = ex
                json_result = failure_response(output)
                return json_result

        else:
            output['reason'] = msg.format('Failed')
            json_result = failure_response(output)
        return json_result

    except Exception as ex:
        print(str(ex))
        output['reason'] = str(ex)
        return failure_response(output)


APP = Flask(__name__)


@APP.route('/check_oms_subs_status', methods=['POST'])  # USED TO TEST.. COMMENT IT WHILE UPLOADING
@cloud_event_decorator(INPUT_TEMPLATE)
def main():
    """
        General description:
        Args:

        Returns:
            Returns result entities that were collected by the atom.
        Example :
        main()
    """
    return handle(request.get_json())


if __name__ == '__main__':  # USED TO TEST.. COMMENT IT WHILE UPLOADING
    APP.run(port=10123, host='0.0.0.0', debug=False)  # USED TO TEST.. COMMENT IT WHILE UPLOADING

