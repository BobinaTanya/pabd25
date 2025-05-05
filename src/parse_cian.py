"""Parse data from cian.ru"""
import datetime
import cianparser
import pandas as pd

moscow_parser = cianparser.CianParser(location="Москва")

def main():
    """
    Парсим 1, 2 и 3-комнатные квартиры
    """
    t = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    # Парсим каждый тип квартир отдельно и объединяем результаты
    all_data = []
    
    for room_type in [1, 2, 3]:  # Перебираем 1, 2 и 3 комнатные
        print(f"Парсим {room_type}-комнатные квартиры...")
        
        data = moscow_parser.get_flats(
            deal_type="sale",
            rooms=(room_type,),  # Кортеж с одним элементом
            with_saving_csv=False,
            additional_settings={
                "start_page": 1,
                "end_page": 25,  
                "object_type": "secondary"
            })
        
        all_data.extend(data)
    
    # Сохраняем все данные в один файл
    df = pd.DataFrame(all_data)
    csv_path = f'data/raw/1-2-3-room_{t}.csv'
    df.to_csv(csv_path, encoding='utf-8', index=False)
    print(f"Данные сохранены в {csv_path}")

if __name__ == '__main__':
    main()