from flask import Flask, render_template, redirect, request, url_for, session
import pymysql.cursors
import os

# Ini Inisialisasi kode flask 
app = Flask(__name__)
app.secret_key = 'SECRETKEY'
app.config['UPLOAD_FOLDER'] = r"X:\Python File\Arkatex - Proforma - Invoice - Project\uploads"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inisialisasi Database Terlebih dahulu
db_config = {

    'host' : 'localhost', # dikarenakan lokal jadi pake PHPmyadmin local 
    'user': 'root',
    'password': '',
    'db': 'arkatex', # Nama databasenya
    'cursorclass': pymysql.cursors.DictCursor

}

# ini buat penghubung ke database sql 
def create_connection(): 
    return pymysql.connect(**db_config)

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/proforma', methods = ['GET','POST'])
def proforma():
    
    conn   = create_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM products") # Query untuk menampilkan semua employee yang sudah di add
    data   = cursor.fetchall() # Ini biar nangkep semua atribut yang ada di database tampa terkecuali
    
    conn.close()
    return render_template('proforma.html', data=data)


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    conn = create_connection()  # Koneksi ke database
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        # Ambil semua tipe produk untuk dropdown
        cursor.execute("SELECT id, nama_tipe, harga_tipe FROM tipe_produk")
        tipe_produk = cursor.fetchall()

        # Ambil data dari form
        nama_produk = request.form['nama_produk']
        tipe_id = request.form['tipe_id']
        lebar = request.form['lebar']
        panjang = request.form['panjang']
        harga = ""
        notes = request.form.get('notes', '')  # default string kosong

        # Ambil harga berdasarkan tipe_id
        if tipe_id:
            cursor.execute("SELECT harga_tipe FROM tipe_produk WHERE id = %s", (tipe_id,))
            result = cursor.fetchone()
            harga = result['harga_tipe'] if result else ""

        # Handle upload gambar
        gambar_file = request.files.get('gambar')
        gambar_nama = gambar_file.filename if gambar_file else None
        if gambar_file:
            gambar_file.save(os.path.join(app.config['UPLOAD_FOLDER'], gambar_nama))

        # Insert data jika tombol submit ditekan
        if 'submit' in request.form:
            try:
                cursor.execute("""
                    INSERT INTO products (nama_produk, tipe_id, harga, lebar, panjang, gambar, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (nama_produk, tipe_id, harga, lebar, panjang, gambar_nama, notes))
                conn.commit()
            except Exception as e:
                print(f"Error inserting data: {e}")
                conn.rollback()
                return "Error inserting data", 500

            cursor.close()
            conn.close()
            return redirect(url_for('proforma'))

    
    cursor.execute("SELECT id, nama_tipe FROM tipe_produk")
    tipe_produk = cursor.fetchall()
    cursor.close()
    conn.close()

    # Kirimkan variabel kosong untuk GET
    return render_template('add.html', tipe_produk=tipe_produk, selected_tipe_id=None, selected_harga="")

@app.route('/invoice')
def invoice():
    conn = create_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Hitung total harga
    total_harga = sum([float(product['harga']) for product in data])

    return render_template('invoice.html', data=data, total_harga=total_harga)

@app.route('/delete/<int:id>')
def delete(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute ('DELETE FROM products WHERE id=%s', (id))
    conn.commit()
    conn.close()
    return redirect(url_for('proforma'))

if __name__ == '__main__': # Ini kode penutup Flask selalu harus ada (jika tidak ada program tidak akan berjalan)
    app.run(debug=True)