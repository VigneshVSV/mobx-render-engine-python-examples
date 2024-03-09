from hololinked.system_host import create_system_host
from hololinked.system_host.server import start_tornado_server
from pathlib import Path
import os
import ssl

from pages import GentecPageHandler

ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    f'{str(Path(os.path.dirname(__file__)).parent)}{os.sep}assets{os.sep}security{os.sep}certificate.pem',
    keyfile=f'{str(Path(os.path.dirname(__file__)).parent)}{os.sep}assets{os.sep}security{os.sep}key.pem'
)

server = create_system_host(
    f"{str(Path(os.path.dirname(__file__)).parent)}{os.sep}assets{os.sep}db_config.json", 
    ssl_context=ssl_context, CORS=["https://localhost:5173"],
    handlers=[
        (r"/dashboards/optical-energy-meter", GentecPageHandler)
    ]
)
start_tornado_server(server, port=8081)