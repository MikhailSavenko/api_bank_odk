import json


def is_payment_in_txt(payment_to_check):
    file_path = "payments.txt"
    with open(file_path, 'r') as file:
        for line in file:
            payment_data = json.loads(line)
            if payment_data == payment_to_check:
                return True
    return False


def payment_write_in_txt(result_payments):
    file_path = "payments.txt"
    payment_data_str = json.dumps(result_payments)
    with open(file_path, 'w') as file:
        file.write(payment_data_str)
    return payment_data_str