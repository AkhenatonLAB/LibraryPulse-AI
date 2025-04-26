import firebase_admin
from firebase_admin import credentials, db
import csv

# 1. Firebase bağlantısı kurma
cred = credentials.Certificate('serviceAccountKey.json')  # Service Account Key JSON dosyanız
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://librarypulse-2f7e9-default-rtdb.europe-west1.firebasedatabase.app/'
})

# 2. CSV'den sayıyı okuma
def read_number_from_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            row = next(reader)  # İlk satırı al
            number = int(row[0])  # İlk sütundaki sayıyı al
            return number
    except Exception as e:
        print(f"Hata: CSV okuma sırasında bir sorun oluştu: {e}")
        return None

# 3. Firebase'e yeni sayıyı gönderme
def set_number_of_people(new_value):
    ref = db.reference('number_of_people')  # Firebase'deki 'number_of_people' alanına referans
    ref.set(new_value)  # Yeni değeri (PUT) olarak gönder
    print(f"Başarıyla 'number_of_people' değeri {new_value} olarak güncellendi.")

if __name__ == "__main__":
    # CSV'den sayıyı oku
    csv_file = 'number_of_people.csv'  # CSV dosyasının yolu
    new_value = read_number_from_csv(csv_file)
    
    if new_value is not None:
        # Sayıyı Firebase'e gönder
        set_number_of_people(new_value)
    else:
        print("CSV'den geçerli bir sayı okunamadı.")
