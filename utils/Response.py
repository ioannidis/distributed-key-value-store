import pickle


class Response:

    def __init__(self, code=200, status='OK', payload='') -> None:
        self.code = code
        self.status = status
        self.payload = payload
        self.response = self.generate_response()

    def generate_response(self):
        res = {
            'code': self.code,
            'status': self.status,
            'payload': self.payload
        }

        return pickle.dumps(res)

    def get_response(self):
        return self.response

    def get_options(self):
        res = {
            'req_type': 'OPTIONS',
            'res_size': len(self.response)
        }

        return pickle.dumps(res)
