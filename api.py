# api.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Rota para obter informações de um equipamento com base no número de série da TAG
@app.route('/api/equipamento/<numero_serie>', methods=['GET'])
def obter_informacoes_equipamento(numero_serie):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    # Consulta para obter informações do equipamento com base no número de série da TAG
    cursor.execute("SELECT * FROM equipamentos WHERE numero_serie_tag=?", (numero_serie,))
    equipamento = cursor.fetchone()

    conn.close()

    if equipamento:
        # Converte os dados do equipamento para um dicionário
        equipamento_dict = {
            'id': equipamento[0],
            'empresa_id': equipamento[1],
            'modelo': equipamento[2],
            'numero_serie': equipamento[3],
            'numero_serie_tag': equipamento[4],
            'latitude': equipamento[5],
            'longitude': equipamento[6],
            'setor_id': equipamento[7]
        }

        return jsonify(equipamento_dict)
    else:
        return jsonify({'mensagem': 'Equipamento não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)

