# data_manager.py
import pandas as pd
import os

def normalize_phone_numbers(phone_str):
    return phone_str.replace(',', ' ').replace(' ', '')

def normalize_emails(email_str):
    return email_str.lower()

class DataManager:
    def __init__(self, output_file='companies.csv'):
        self.output_file = output_file
        self.load_existing_records()

    def load_existing_records(self):
        if os.path.exists(self.output_file):
            self.df = pd.read_csv(self.output_file)
            self.existing_records = set(map(tuple, self.df.values))
        else:
            self.existing_records = set()
            self.init_csv()

    def init_csv(self):
        columns = [
            'Nombre', 'Descripción', 'Servicios', 'Teléfonos', 'Dirección', 'Sitio web',
            'Horario', 'Búsqueda', 'Localidad'
        ]
        self.df = pd.DataFrame(columns=columns)

    def is_valid_record(self, record):
        essential_fields = ['Nombre', 'Teléfonos', 'Dirección']
        return all(record.get(field) for field in essential_fields)

    def is_duplicate_record(self, record):
        return tuple(record.values()) in self.existing_records

    def write_to_csv(self, data):
        if self.is_valid_record(data) and not self.is_duplicate_record(data):
            if 'Teléfonos' in data.keys():
                data['Teléfonos'] = normalize_phone_numbers(data['Teléfonos'])
            if 'Emails' in data.keys():
                data['Emails'] = normalize_emails(data['Emails'])
            self.existing_records.add(tuple(data.values()))
            self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True)
            self.df.to_csv(self.output_file, index=False)
