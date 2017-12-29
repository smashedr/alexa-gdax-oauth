
def error_resp(error_code, error_msg):
    resp = {'ErrorCode': error_code, 'Error': error_msg}
    return resp
