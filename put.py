import os
import csv
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)

# Firebase bağlantısını kur
cred = credentials.Certificate('serviceAccountKey.json')  # Firebase Admin SDK JSON dosyası
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')  # .env dosyasındaki Firebase URL'sini kullan
})

# CSV'den sayıyı oku
def read_number_from_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            # CSV'nin ilk satırını okuyalım (veya istediğiniz satırı)
            row = next(reader)
            number = int(row[0])  # CSV'deki ilk sütundaki sayıyı al
            return number
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

@app.route('/update_people_count', methods=['PUT'])
def update_people_count():
    # CSV'den sayıyı oku
    csv_file = 'people_count.csv'  # CSV dosyasının yolu
    new_count = read_number_from_csv(csv_file)
    #new_count = 22 bu kısmı ai ile birlikte değiştir
    
    if new_count is None:
        return jsonify({"error": "Failed to read number from CSV"}), 400
    
    # Firebase'deki veriyi güncelle
    ref = db.reference('number_of_people')  # Firebase'deki verinin yolu
    ref.set(new_count)  # Yeni değeri Firebase'e kaydediyoruz

    return jsonify({"message": "People count updated successfully", "number_of_people": new_count}), 200

if __name__ == '__main__':
    app.run(debug=True)
