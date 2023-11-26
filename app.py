from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
from io import BytesIO
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    column_name_options = []
    filename = None
    data = None

    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # Baca data CSV untuk mengidentifikasi nama kolom
            data = read_file(file_path)
            if data is not None:
                column_names = data.columns.tolist()
                column_name_options = [{'name': name, 'value': name} for name in column_names];

                # Pilih nama kolom berdasarkan permintaan pengguna
                column_name = request.form.get('column_name')
                

                if column_name:
                    if column_name in column_names:
                        # Lanjutkan dengan analisis berdasarkan kolom yang dipilih oleh pengguna
                        graph_type = request.form.get('graph_type')
                        if graph_type == 'bar':
                            bar_graph = create_bar_graph(data, column_name)
                            plot_url = plot_to_base64(bar_graph)
                        elif graph_type == 'pie':
                            pie_chart = create_pie_chart(data, column_name)
                            plot_url = plot_to_base64(pie_chart)
                        else:
                            plot_url = None

                        return render_template('index.html', column_name_options=column_name_options, filename=filename, data=data.to_html(), plot_url=plot_url)

    return render_template('index.html', column_name_options=column_name_options, filename=filename, data=data)

def read_file(file_path):
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    else:
        data = None

    return data

def create_bar_graph(data, column_name):
    # Buat grafik batang
    plt.figure(figsize=(8, 6))
    plt.bar(data.index, data[column_name])
    plt.title(f'Analisis: {column_name}')
    plt.xlabel('Indeks Data')
    plt.ylabel(column_name)
    return plt

def create_pie_chart(data, column_name):
    # Ambil dua kategori pertama
    top_two_categories = data[column_name].head(2)
    # Hitung total perbandingan
    total = top_two_categories.sum()
    # Hitung perbandingan relatif untuk dua kategori tersebut
    relative_ratios = top_two_categories / total * 100

    # Buat label menggunakan nama kolom yang dipilih
    labels = [f'{column_name}: {relative_ratios[i]:.1f}%' for i in range(len(top_two_categories))]

    # Buat diagram pie dengan dua kategori
    plt.figure(figsize=(8, 6))
    plt.pie(top_two_categories, labels=labels, autopct='%1.1f%%')
    plt.title(f'Diagram Pie: {column_name}')
    return plt


def plot_to_base64(plt):
    # Ubah gambar plot menjadi base64 untuk ditampilkan di halaman HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    plt.close()
    return base64.b64encode(plot_data).decode()


if __name__ == '__main__':
    app.run(debug=True)
