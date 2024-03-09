from hololinked.system_host.handlers import for_authenticated_user, SystemHostHandler
from hololinked.server import JSONSerializer
from dashboard import Dashboard

D = Dashboard()

serializer = JSONSerializer()

class GentecPageHandler(SystemHostHandler):

    def get(self):
        self.set_status(200)
        self.set_header("content-type", "application/json")
        self.write(serializer.dumps(D))
        self.set_custom_default_headers()
        self.finish()

    def options(self):
        self.set_status(204)
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.set_custom_default_headers()
        self.finish()

