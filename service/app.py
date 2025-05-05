from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
from pathlib import Path
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler('flask.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация
MODEL_PATH = Path('linear_regression_model.pkl')  

class SimpleModel:
    """Резервная модель если основная не загрузится"""
    def predict(self, X):
        return np.array([x[0] * 100000 for x in X])  

def load_model():
    """Загрузка модели с резервным вариантом"""
    try:
        if not MODEL_PATH.exists():
            logger.warning("Файл модели не найден, используется резервная модель")
            return SimpleModel()
        
        model = joblib.load(MODEL_PATH)
        
        # Проверка что модель имеет метод predict
        if not hasattr(model, 'predict'):
            logger.warning("Загруженный объект не является моделью, используется резервная")
            return SimpleModel()
            
        logger.info("Модель успешно загружена")
        return model
        
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {str(e)}")
        return SimpleModel()

# Инициализация модели
model = load_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Валидация и преобразование данных
        try:
            area = float(data.get('area', 0))
            rooms = int(data.get('rooms', 1))
            floor = int(data.get('floor', 1))
            total_floors = int(data.get('total_floors', 5))
        except ValueError:
            return jsonify({'error': 'Invalid parameter types'}), 400

        # Проверка логики
        if area <= 0:
            return jsonify({'error': 'Area must be positive'}), 400
        if floor > total_floors:
            return jsonify({'error': 'Floor cannot exceed total floors'}), 400

        # Предсказание
        prediction = model.predict([[area, rooms, floor, total_floors]])[0]
        price = round(float(prediction), 2)
        
        return jsonify({
            'price': price,
            'currency': 'RUB',
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting server...")
    logger.info(f"Model type: {type(model)}")
    app.run(host='0.0.0.0', port=5050)