"""
Insert order in temp table via AutoTicketResolution
"""

'''
Developers need to make sure the input json will be of below format
This is the input template that will be validated
'''

INPUT_TEMPLATE = {
    "data": {
        "flowName": "",
        "company": "",
        "project": "",
        "parameters": [
            {"source_machine": {"entity": ""}},
            {"order_id": ""}]
    }
}

'''
json_input --> is a request dict.There is no need to run "json.loads()" on it
The response has to be of type dict/list and we need to return it as "json_result"
from the "main()" def all the business logic will be written in "handle()"
'''


def handle(json_input):
    
    orig_order_id = extract_parameters(json_input).get('order_id')
    if orig_order_id[-1] == 'A':
        order_id = orig_order_id[:-1]
    else:
        order_id = orig_order_id

    drop_qry = """drop table PENDING_ORDER_DATA1"""
    insert_query = "INSERT INTO PENDING_ORDER_DATA1 (order_id) values ('"+str(order_id)+"')"
    crt_qry = """create table PENDING_ORDER_DATA1 (order_id varchar(20))"""

    config_details = extract_parameters(json_input).get('source_machine')
    print(config_details)
    output = {}
    try:
        status0, data0 = run_dml_query(config_details, drop_qry,timeout=60000, additional_conn_params={"bypass_validation_ind": True})
        print("data0: "+ str(data0))

        status1, data1 = run_dml_query(config_details, crt_qry, timeout=60000)
        print("data1: "+ str(data1))

        status, data = run_dml_query(config_details, insert_query)
        print("Status: "+status)
        print("data: "+ str(data))

        if status == constants.get_success() and status1 == constants.get_success():
            output['output'] = str(data)
            json_result = success_response(output)
        else:
            output['output'] = str(data)
            output['reason'] = str(data)
            json_result = failure_response(output)
        return json_result

    except Exception as ex:
        output['reason'] = str(ex)
        return failure_response(output)


# '''
# Fission is invoking the main() method.
# The input payload validation is being done in execut() decorator
# The main job is being done by the handle definition
# '''

APP = Flask(__name__)  # USED TO TEST.. COMMENT IT WHILE UPLOADING


# USED TO TEST.. COMMENT IT WHILE UPLOADING
@APP.route('/check', methods=['POST'])
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
    # USED TO TEST.. COMMENT IT WHILE UPLOADING
    APP.run(port=1013, host='0.0.0.0', debug=True)

