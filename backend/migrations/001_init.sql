-- CloudSanté - Migration initiale
-- (c) 2024 CloudSante SAS

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    email VARCHAR(255),
    last_login DATETIME,
    failed_attempts INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table des patients
CREATE TABLE IF NOT EXISTS patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    date_naissance DATE NOT NULL,
    num_secu VARCHAR(15) NOT NULL,
    diagnostic TEXT NOT NULL,
    medecin VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table du journal d'audit
CREATE TABLE IF NOT EXISTS audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(255),
    details TEXT,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des sessions
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des fichiers
CREATE TABLE IF NOT EXISTS files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    filename VARCHAR(255),
    filepath VARCHAR(500),
    file_type VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Insertion des utilisateurs par défaut
INSERT INTO users (username, password, role, email) VALUES
('admin', '5f4dcc3b5aa765d61d8327deb882cf99', 'admin', 'admin@cloudsante.fr'),
('backup_svc', '81dc9bdb52d04dc20036dbd8313ed055', 'admin', 'backup@cloudsante.fr'),
('acme_admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', 'admin@acme-industries.fr'),
('export_cron', '827ccb0eea8a706c4c34a16891f84e7b', 'admin', 'cron@cloudsante.fr'),
('test', '098f6bcd4621d373cade4e832627b4f6', 'admin', 'test@cloudsante.fr'),
('medecin_dupont', 'e10adc3949ba59abbe56e057f20f883e', 'medecin', 'dupont@cloudsante.fr'),
('infirmier_martin', '5d41402abc4b2a76b9719d911017c592', 'infirmier', 'martin@cloudsante.fr'),
-- Comptes avec email comme username (pour le login via le front)
('dr.dupont@hopital.fr', '0b54a8c45b6d7c6fd598a0ea6c796534', 'doctor', 'dr.dupont@hopital.fr'),
('admin@cloudsante.fr', '0f9b8be64550f3013ef959fb1f8dc8b4', 'admin', 'admin@cloudsante.fr');

-- Insertion de patients fictifs (données sensibles en clair)
INSERT INTO patients (nom, prenom, date_naissance, num_secu, diagnostic, medecin) VALUES
('Dubois', 'Jean', '1975-03-15', '1750315123456', 'Hypertension artérielle - Traitement par Lisinopril 10mg', 'Dr. Dupont'),
('Martin', 'Marie', '1982-07-22', '2820722987654', 'Diabète type 2 - HbA1c: 7.2% - Metformine 500mg x2', 'Dr. Dupont'),
('Bernard', 'Pierre', '1968-11-08', '1681108456789', 'Cancer du côlon stade II - En chimiothérapie FOLFOX', 'Dr. Lefevre'),
('Durand', 'Sophie', '1995-05-30', '2950530234567', 'Dépression majeure - Sertraline 100mg - Suivi psy hebdo', 'Dr. Moreau'),
('Petit', 'Luc', '1960-09-12', '1600912345678', 'Insuffisance cardiaque - BNP: 450 pg/ml - Bisoprolol + Furosémide', 'Dr. Simon'),
('Laurent', 'Anne', '1988-01-25', '2880125567890', 'Hypothyroïdie - TSH: 2.1 mUI/L - Levothyroxine 75µg', 'Dr. Thomas'),
('David', 'Marc', '1970-12-03', '1701203678901', 'BPCO stade III - FEV1: 35% - Oxygénothérapie 2L/min', 'Dr. Dupont'),
('Moreau', 'Claire', '1992-06-18', '2920618789012', 'Asthme allergique - Fluticasone 250µg x2 + Salbutamol PRN', 'Dr. Lefevre');

-- Création d'index
CREATE INDEX idx_patients_num_secu ON patients(num_secu);
CREATE INDEX idx_patients_nom ON patients(nom);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
