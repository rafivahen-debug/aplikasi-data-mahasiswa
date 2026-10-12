from datetime import date
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = "ganti-dengan-secret-key-anda"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "mahasiswa.db"


def get_db_connection():
    """Membuka koneksi ke database SQLite."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Membuat tabel mahasiswa jika belum tersedia."""
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                nim INTEGER PRIMARY KEY,
                nama TEXT NOT NULL,
                program_studi TEXT NOT NULL,
                angkatan INTEGER NOT NULL,
                ipk REAL NOT NULL CHECK (ipk >= 0 AND ipk <= 4)
            )
        """)
        connection.commit()


def calculate_lama_studi(angkatan):
    """Menghitung lama studi berdasarkan tahun saat ini."""
    return date.today().year - angkatan


def validate_mahasiswa(form, creating=True, current_nim=None):
    """Memeriksa input dan mengembalikan data bersih atau pesan error."""
    nim_raw = form.get("nim", "").strip()
    nama = form.get("nama", "").strip()
    program_studi = form.get("program_studi", "").strip()
    angkatan_raw = form.get("angkatan", "").strip()
    ipk_raw = form.get("ipk", "").strip()

    if not nim_raw or not nama or not program_studi or not angkatan_raw or not ipk_raw:
        return None, "Semua kolom wajib diisi."

    try:
        nim = int(nim_raw)
        if nim <= 0:
            return None, "NIM harus berupa bilangan bulat positif."
    except ValueError:
        return None, "NIM harus berupa bilangan bulat."

    try:
        angkatan = int(angkatan_raw)
    except ValueError:
        return None, "Angkatan harus berupa bilangan bulat."

    if angkatan < 1900 or angkatan > date.today().year:
        return None, f"Angkatan harus antara 1900 dan {date.today().year}."

    try:
        ipk = float(ipk_raw.replace(",", "."))
    except ValueError:
        return None, "IPK harus berupa angka antara 0,00 dan 4,00."

    if not 0 <= ipk <= 4:
        return None, "IPK harus berada dalam rentang 0,00 sampai 4,00."

    connection = get_db_connection()
    try:
        existing = connection.execute(
            "SELECT nim FROM mahasiswa WHERE nim = ?", (nim,)
        ).fetchone()
        if existing and (creating or nim != current_nim):
            return None, f"NIM {nim} sudah terdaftar. Gunakan NIM yang berbeda."
    finally:
        connection.close()

    return {
        "nim": nim,
        "nama": nama,
        "program_studi": program_studi,
        "angkatan": angkatan,
        "ipk": ipk,
    }, None


@app.route("/")
def index():
    connection = get_db_connection()
    mahasiswa = connection.execute(
        "SELECT * FROM mahasiswa ORDER BY nim"
    ).fetchall()
    connection.close()

    rows = []
    for item in mahasiswa:
        row = dict(item)
        row["lama_studi"] = calculate_lama_studi(row["angkatan"])
        rows.append(row)

    return render_template("index.html", mahasiswa=rows, tahun=date.today().year)


@app.route("/mahasiswa/tambah", methods=["GET", "POST"])
def tambah_mahasiswa():
    if request.method == "POST":
        data, error = validate_mahasiswa(request.form)
        if error:
            flash(error, "error")
            return render_template("form.html", mode="tambah", data=request.form, tahun_sekarang=date.today().year)

        connection = get_db_connection()
        try:
            connection.execute("""
                INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk)
                VALUES (?, ?, ?, ?, ?)
            """, (data["nim"], data["nama"], data["program_studi"],
                  data["angkatan"], data["ipk"]))
            connection.commit()
        except sqlite3.IntegrityError:
            flash("Data gagal disimpan karena NIM sudah terdaftar atau data tidak valid.", "error")
            return render_template("form.html", mode="tambah", data=request.form, tahun_sekarang=date.today().year)
        finally:
            connection.close()

        flash("Data mahasiswa berhasil ditambahkan.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", mode="tambah", data={}, tahun_sekarang=date.today().year)


@app.route("/mahasiswa/<int:nim>")
def detail_mahasiswa(nim):
    connection = get_db_connection()
    mahasiswa = connection.execute(
        "SELECT * FROM mahasiswa WHERE nim = ?", (nim,)
    ).fetchone()
    connection.close()

    if mahasiswa is None:
        abort(404)

    data = dict(mahasiswa)
    data["lama_studi"] = calculate_lama_studi(data["angkatan"])
    return render_template("detail.html", mahasiswa=data)


@app.route("/mahasiswa/<int:nim>/edit", methods=["GET", "POST"])
def edit_mahasiswa(nim):
    connection = get_db_connection()
    existing = connection.execute(
        "SELECT * FROM mahasiswa WHERE nim = ?", (nim,)
    ).fetchone()
    connection.close()

    if existing is None:
        abort(404)

    if request.method == "POST":
        data, error = validate_mahasiswa(request.form, creating=False, current_nim=nim)
        if error:
            flash(error, "error")
            return render_template("form.html", mode="edit", data=request.form,
                                   nim_asal=nim, tahun_sekarang=date.today().year)

        connection = get_db_connection()
        try:
            connection.execute("""
                UPDATE mahasiswa
                SET nim = ?, nama = ?, program_studi = ?, angkatan = ?, ipk = ?
                WHERE nim = ?
            """, (data["nim"], data["nama"], data["program_studi"],
                  data["angkatan"], data["ipk"], nim))
            connection.commit()
        except sqlite3.IntegrityError:
            flash("Perubahan gagal disimpan. Pastikan NIM unik dan IPK valid.", "error")
            return render_template("form.html", mode="edit", data=request.form,
                                   nim_asal=nim, tahun_sekarang=date.today().year)
        finally:
            connection.close()

        flash("Data mahasiswa berhasil diperbarui.", "success")
        return redirect(url_for("detail_mahasiswa", nim=data["nim"]))

    return render_template("form.html", mode="edit", data=dict(existing), nim_asal=nim, tahun_sekarang=date.today().year)


@app.route("/mahasiswa/<int:nim>/hapus", methods=["POST"])
def hapus_mahasiswa(nim):
    connection = get_db_connection()
    cursor = connection.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))
    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        abort(404)

    flash("Data mahasiswa berhasil dihapus.", "success")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
