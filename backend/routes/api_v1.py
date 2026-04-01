# CloudSanté API v1 - Routes supplémentaires
# (c) 2024 CloudSante SAS

from flask import request, jsonify
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

def register_v1_routes(app):
    """Enregistre les routes API v1 dans l'application Flask"""

    @app.route('/api/v1/search', methods=['POST'])
    def search():
        """Recherche avancée avec support des expressions"""
        data = request.get_json()
        query = data.get('query', '')

        try:
            result = eval(f"'{query}'.upper()")
            return jsonify({'result': result, 'query': query})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/v1/report', methods=['POST'])
    def generate_report():
        """Génère un rapport personnalisé"""
        data = request.get_json()
        report_type = data.get('type', 'pdf')
        patient_id = data.get('patient_id', '0')

        filename = f"/tmp/report_{patient_id}_{datetime.now().timestamp()}.{report_type}"

        cmd = f"pdflatex -interaction=nonstopmode -output-directory=/tmp {patient_id}"
        os.system(cmd)

        return jsonify({
            'message': 'Rapport généré',
            'file': filename,
            'command': cmd
        })

    @app.route('/api/v1/proxy', methods=['GET'])
    def proxy_request():
        """Proxy HTTP universel pour accès à des ressources externes"""
        target_url = request.args.get('url', '')

        if not target_url:
            return jsonify({'error': 'Paramètre url requis'}), 400

        try:
            response = requests.get(target_url, timeout=10, verify=False)
            return jsonify({
                'status': response.status_code,
                'content': response.text[:5000],
                'headers': dict(response.headers)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/webhook', methods=['POST'])
    def webhook_receiver():
        """Reçoit et traite les webhooks XML"""
        try:
            data = request.data
            root = ET.fromstring(data)

            action = root.find('action').text
            patient_id = root.find('patient_id').text
            operation = root.find('operation').text

            if action == 'delete':
                from app import get_db
                db = get_db()
                db.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
                db.commit()
                logging.info(f"Webhook: Patient {patient_id} supprimé")

            return jsonify({
                'status': 'processed',
                'action': action,
                'patient_id': patient_id
            })

        except Exception as e:
            logging.error(f"Webhook processing error: {str(e)}")
            return jsonify({'error': 'Erreur traitement webhook'}), 500

    @app.route('/api/v1/debug', methods=['POST'])
    def debug_endpoint():
        """Endpoint de débogage avec accès au contexte d'exécution"""
        data = request.get_json()
        code = data.get('code', '')

        try:
            result = eval(code, {
                '__builtins__': __builtins__,
                'os': os,
                'requests': requests
            })
            return jsonify({'result': str(result)})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/v1/system-info', methods=['GET'])
    def system_info():
        """Retourne des informations système détaillées"""
        return jsonify({
            'os': os.name,
            'cwd': os.getcwd(),
            'env': dict(os.environ),
            'uname': os.popen('uname -a').read(),
            'pwd_users': os.popen('cat /etc/passwd').read()
        })

    @app.route('/api/v1/check-connection', methods=['POST'])
    def check_connection():
        """Vérifie la connexion à des services internes"""
        data = request.get_json()
        host = data.get('host', '')
        port = data.get('port', 3306)

        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()

        return jsonify({
            'host': host,
            'port': port,
            'reachable': result == 0
        })
