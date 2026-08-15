import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Referências para os dados partilhados
shared_telemetry = {}
shared_missions = {}


class RequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            telemetry_dict = {}
            telemetry_snapshot = shared_telemetry.copy()

            for rover_id, tel_obj in telemetry_snapshot.items():
                telemetry_dict[rover_id] = {
                    "bateria": getattr(tel_obj, 'bateria', 0),
                    "temperatura": getattr(tel_obj, 'temperatura', 0),
                    "coordenadas": getattr(tel_obj, 'coordenadas', (0, 0)),
                    "estado": getattr(tel_obj, 'estado', 'Unknown')
                }

            response_data = {
                "telemetry": telemetry_dict,
                "missions": list(shared_missions.values())
            }

            # 2. Enviar JSON
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            # Rota não encontrada
            self.send_error(404, "Endpoint not found")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass


def configure_api(telemetry_ref, missions_ref):
    global shared_telemetry, shared_missions
    shared_telemetry = telemetry_ref
    shared_missions = missions_ref


def run_api(host='0.0.0.0', port=5000):
    server = ThreadedHTTPServer((host, port), RequestHandler)
    # print(f"[API] Servidor HTTP nativo a correr em {host}:{port}...")
    server.serve_forever()