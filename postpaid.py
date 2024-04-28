INPUT_TEMPLATE = {
    "data": {
        "flowName": "",
        "company": "",
        "project": "",
        "parameters": [
            {"card_number": ""}
        ]
    }

}



def handle(json_input):

    parameters = extract_parameters(json_input)
    source_db = str(search_cm('env'))
    card_number = parameters.get('card_number')

    try:
        main_id = "select distinct main_id from item_data where service_no ='{card_number}' and main_ind ='1' and STATUS='AC' and end_date>sysdate".format(card_number=card_number)

        config_details = extract_parameters(json_input).get('source_machine')
        status, data = run_select_query(source_db, main_id)
        output = {}
        print("DATA TYPE", type(data))
        output = {}

        if status == constants.get_success():
            count = 0
            main_id = ' '
            curr_row = data[1][count]

            if main_id != curr_row.get('MAIN_ID'):
                main_id = curr_row.get('MAIN_ID')

            print("Original data: " + str(data[1]) +", main_id: " + str(main_id))


            graphical_id = "select graphical_id from request_data where smart_card_id ='{card_number}' and ROWNUM=1 and activity_name='refresh' and subscriber_no ='{main_id}' and trunc(SYS_CREATION_DATE)= TRUNC(SYSDATE) order by SYS_CREATION_DATE desc".format(main_id=main_id, card_number=card_number)

            status1, data1 = run_select_query(source_db, graphical_id)
            if status1 == constants.get_success():
                count1 = 0
                graphical_id1 = ' '
                curr_row1 = data1[1][count1]
                graphical_id1 = curr_row1.get('graphicsl_id')
                print("Original data: " + str(data1[1]) +", graphicsl_id: " + str(graphical_id1))

                select_channel_details = "select CHANNEL_DETAILS from acp_request_details where graphical_id ='{graphical_id1}' and CHANNEL_DETAILS like '%offerKey%'".format(graphical_id1=graphical_id1)

                status2, data2 = run_select_query(source_db, select_channel_details)
                if status2 == constants.get_success():
                    count2 = 0
                    channel_details = ' '
                    curr_row2 = data2[1][count2]
                    channel_details = curr_row2.get('CHANNEL_DETAILS')
                    print("Original data: " + str(data2[1]) +", select_channel_details: " + str(channel_details))


            data = str(data2)

            output['output'] = str(data2)
            json_result = success_response({"final_data": data})
        else:
            fail_st = "Failed!"
            output['reason'] = str(data)
            json_result = failure_response({"final_data": fail_st})
        return json_result

    except Exception as ex:
        output['reason'] = str(ex)
        return failure_response(output)



# '''
# Fission is invoking the main() method.
# Please do not change anything below this method declation or body
# The input payload validation is being done in execut() decorator
# The main job is being done by the handle definition
# '''
APP = Flask(__name__)  # USED TO TEST.. COMMENT IT WHILE UPLOADING


# USED TO TEST.. COMMENT IT WHILE UPLOADING
@APP.route('/check', methods=['POST'])
@cloud_event_decorator(INPUT_TEMPLATE)
def main():
    '''
        General description:
        No description
        MinPlatformVersion:20.6
        Args:

        Returns:
            Returns result entities that were collected by the atom.
        Example :
        main()
    '''
    return handle(request.get_json())


if __name__ == '__main__':  # USED TO TEST.. COMMENT IT WHILE UPLOADING
    # USED TO TEST.. COMMENT IT WHILE UPLOADING
    APP.run(port=1012, host='0.0.0.0', debug=True)
