from . import Session
from .models import Service
from sqlalchemy import func

def add_hotel_services():
    session = Session()
    try:
        # Удаляем дубликаты, оставляя только записи с минимальным ID для каждого названия
        duplicates = session.query(Service.name, func.min(Service.id).label('min_id')).\
            group_by(Service.name).\
            having(func.count(Service.id) > 1).\
            all()
        
        for name, min_id in duplicates:
            # Удаляем все записи с таким названием, кроме записи с минимальным ID
            session.query(Service).\
                filter(Service.name == name, Service.id != min_id).\
                delete(synchronize_session=False)
        
        # Получаем список существующих услуг после удаления дубликатов
        existing_services = session.query(Service).all()
        existing_names = [service.name for service in existing_services]
        
        # Определяем базовые ��слуги
        services_to_add = [
            {
                'name': 'Завтрак',
                'description': 'Завтрак в ресторане отеля (стоимость за сутки)',
                'price': 1000
            },
            {
                'name': 'Ужин',
                'description': 'Ужин в ресторане отеля (стоимость за сутки)',
                'price': 1500
            },
            {
                'name': 'Дополнительное место',
                'description': 'Дополнительное спальное место в номере (стоимость за сутки проживания)',
                'price': 1500
            }
        ]
        
        # Добавляем только те услуги, которых еще нет
        for service_data in services_to_add:
            if service_data['name'] not in existing_names:
                new_service = Service(
                    name=service_data['name'],
                    description=service_data['description'],
                    price=service_data['price']
                )
                session.add(new_service)
                print(f"Добавлена услуга: {service_data['name']}")
            else:
                # Обновляем существующую услугу
                existing_service = session.query(Service).\
                    filter(Service.name == service_data['name']).\
                    first()
                existing_service.description = service_data['description']
                existing_service.price = service_data['price']
                print(f"Обновлена существующая услуга: {service_data['name']}")
        
        session.commit()
        print("Операция успешно завершена")
        
    except Exception as e:
        print(f"Ошибка при работе с услугами: {e}")
        session.rollback()
    finally:
        session.close() 