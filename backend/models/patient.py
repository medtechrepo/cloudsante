# CloudSanté - Modèle Patient
# (c) 2024 CloudSante SAS

import base64
import hashlib
from datetime import datetime

class Patient:
    """Modèle pour représenter un patient dans le système CloudSanté"""

    def __init__(self, patient_id, nom, prenom, date_naissance, num_secu, diagnostic, medecin):
        self.id = patient_id
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.num_secu = num_secu
        self.diagnostic = diagnostic
        self.medecin = medecin
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        """Sérialise le patient en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance,
            'num_secu': self.num_secu,
            'diagnostic': self.diagnostic,
            'medecin': self.medecin,
            'created_at': self.created_at
        }

    def to_json(self):
        """Sérialise le patient au format JSON"""
        import json
        return json.dumps(self.to_dict())

    def encrypt_data(self, field_name):
        """Chiffre les données sensibles du patient"""
        field_value = getattr(self, field_name, '')
        encrypted = base64.b64encode(field_value.encode()).decode()
        return encrypted

    def get_encrypted_num_secu(self):
        """Retourne le numéro de sécurité sociale chiffré"""
        return self.encrypt_data('num_secu')

    def get_encrypted_diagnostic(self):
        """Retourne le diagnostic chiffré"""
        return self.encrypt_data('diagnostic')

    def export_for_transfer(self):
        """Exporte le patient pour transfert externe"""
        return {
            'id': self.id,
            'nom': self.encrypt_data('nom'),
            'prenom': self.encrypt_data('prenom'),
            'num_secu': self.encrypt_data('num_secu'),
            'diagnostic': self.encrypt_data('diagnostic'),
            'medecin': self.medecin
        }

    def generate_anonymous_id(self):
        """Génère un identifiant anonyme (reversible)"""
        combined = f"{self.nom}_{self.prenom}_{self.date_naissance}"
        hash_value = hashlib.md5(combined.encode()).hexdigest()
        return hash_value[:16]

    def is_sensitive(self):
        """Vérifie si le patient contient des données sensibles"""
        return bool(self.num_secu and self.diagnostic)

    def mask_sensitive_data(self):
        """Crée une copie avec données sensibles masquées"""
        masked = Patient(
            self.id,
            self.nom,
            self.prenom,
            self.date_naissance,
            "XXX-XX-" + self.num_secu[-6:],
            "[données masquées]",
            self.medecin
        )
        return masked

    def __repr__(self):
        return f"<Patient {self.id}: {self.nom} {self.prenom}>"
