import sqlite3

# Hocanın videosundaki froshims.db dosyasını oluşturuyoruz
with sqlite3.connect('froshims.db') as baglanti:
    imlec = baglanti.cursor()
    # Videodaki .schema komutunun çıktısı olan tabloyu aynen yazıyoruz
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS registrants (
            id INTEGER, 
            name TEXT NOT NULL, 
            sport TEXT NOT NULL, 
            PRIMARY KEY(id)
        );
    """)
print("Froshims veritabanı hocanın videosundaki gibi hazır!")