-- Klinik Dr Fang — synthetic clinic schema (SQLite)
-- All data in this database is INVENTED. No real patients.
-- Right-sized for a single-desk PJ general practice (outline §7).

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS conditions;
DROP TABLE IF EXISTS case_notes;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    id              INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    dob             TEXT    NOT NULL,           -- ISO date
    contact         TEXT,
    registered_date TEXT    NOT NULL,           -- ISO date
    flags           TEXT                        -- allergies / risk flags, free text
);

CREATE TABLE appointments (
    id          INTEGER PRIMARY KEY,
    patient_id  INTEGER NOT NULL REFERENCES patients(id),
    datetime    TEXT    NOT NULL,               -- ISO datetime
    status      TEXT    NOT NULL,               -- 'attended' | 'no-show' | 'cancelled'
    doctor      TEXT    NOT NULL
);

CREATE TABLE case_notes (
    id                   INTEGER PRIMARY KEY,
    patient_id           INTEGER NOT NULL REFERENCES patients(id),
    visit_date           TEXT    NOT NULL,      -- ISO date
    presenting_complaint TEXT    NOT NULL,      -- short symptom phrase
    notes                TEXT,                  -- free-text clinical note
    embedding            TEXT                   -- JSON array (vector) of presenting_complaint
);

CREATE TABLE conditions (
    id              INTEGER PRIMARY KEY,
    patient_id      INTEGER NOT NULL REFERENCES patients(id),
    condition       TEXT    NOT NULL,
    diagnosed_date  TEXT    NOT NULL
);

CREATE TABLE prescriptions (
    id          INTEGER PRIMARY KEY,
    patient_id  INTEGER NOT NULL REFERENCES patients(id),
    drug        TEXT    NOT NULL,
    date        TEXT    NOT NULL,
    repeat      TEXT    NOT NULL                -- 'y' | 'n'
);

CREATE TABLE invoices (
    id          INTEGER PRIMARY KEY,
    patient_id  INTEGER NOT NULL REFERENCES patients(id),
    amount      REAL    NOT NULL,
    issued_date TEXT    NOT NULL,
    paid        TEXT    NOT NULL                -- 'y' | 'n'
);

CREATE INDEX idx_appt_patient   ON appointments(patient_id);
CREATE INDEX idx_appt_datetime  ON appointments(datetime);
CREATE INDEX idx_notes_patient  ON case_notes(patient_id);
CREATE INDEX idx_notes_date     ON case_notes(visit_date);
CREATE INDEX idx_cond_patient   ON conditions(patient_id);
CREATE INDEX idx_presc_patient  ON prescriptions(patient_id);
CREATE INDEX idx_inv_patient    ON invoices(patient_id);
