import pickle


class Request:

    def __init__(self, req_type='GET', payload='') -> None:
        self.req_type = req_type
        self.payload = payload
        self.request = self.generate_request()

    def generate_request(self):
        req = {
            'req_type': self.req_type,
            'payload': self.payload
        }

        return pickle.dumps(req)

    def get_request(self):
        return self.request

    def get_options(self):
        req = {
            'req_type': 'OPTIONS',
            'req_size': len(self.request)
        }

        return pickle.dumps(req)

