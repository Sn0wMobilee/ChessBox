import socket
import pickle
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

class P2PNetwork(QObject):
    """СИГНАЛЫ ДЛЯ СВЯЗИ С GUI"""
    move_received = pyqtSignal(str, str) #(from_pos, to_pos) - получение позиции
    opponent_connected = pyqtSignal()  #получение сигнала о том что противник просто подключился
    opponent_disconnected = pyqtSignal() #получение сигнала о том что противник просто отключился
    status_message = pyqtSignal(str) #получение сигнала о статусе игры
    resign_received = pyqtSignal() #получение сигнала о сдаче противника
    gamemode_received = pyqtSignal(str)  # bullet, blitz, rapid, endless
    rematch_request_received = pyqtSignal()
    rematch_accept_received = pyqtSignal()
    rematch_decline_received = pyqtSignal()

    def __init__(self):
        super().__init__() #наследование методов класса QObject
        self.connection = None #начальный атрибут - сам сокет (активное соединение), через который идет обмен данными. 
                               #У хоста появляется после того как клиент подключился, а у клиента после того как он подключился
        self.is_host = False #начальный атрибут - ты не хост. Присваивается только если ты создаешь комнату
        self.connected = False #начальный атрибут - ты пока что не подключен. Выдается только после подключения
        self.server = None #начальный атрибут - сервера нет
        self.am_i_white = None #начальный атрибут - определения цвета нет. Присваивается только после того как хост создал игру
        self.opponent_color = None #тоже самое что и с предыдущим
        self.is_exiting = False #атрибут о том что противник вышел с помощью кнопки меню или сдачи
        self.is_my_request = False
    def host_game(self, port=5555):
        """СОЗДАТЬ ИГРУ (БЫТЬ СЕРВЕРОМ)"""
        self.am_i_white = True #хост - всегда белый
        self.opponent_color = "black" #противник соответственно черный
        print(f"ХОСТ: я белый, противник чёрный")
        try:
            self.is_host = True #логично, ты становишься хостом
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #назначаем протокол для сервера - IPv4 + TCP (надежно)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #разрешаем переиспользовать порт после закрытия
            self.server.bind(('0.0.0.0', port)) #принять подключения откуда угодно
            self.server.listen(1) #начать слушать, очередь строго на 1 подключение
            self.status_message.emit(f"Ожидание игрока на порту {port}...") #пуск сигнала для обновления gui
            threading.Thread(target=self._accept_connection, daemon=True).start() #запуск фонового потока чтобы не зависнуть.
            return True                                     #daemon = True это означает, что поток сам умрёт при закрытии программы
        except Exception as e: #обработчик исключений
            self.status_message.emit(f"Ошибка: {e}")
            return False

    def join_game(self, ip, port=5555):
        """ПОДКЛЮЧИТЬСЯ К ИГРЕ"""
        try:
            self.is_host = False #тот кто подключается соответственно не хост
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #назначаем тот же протокол соединения, что и для сервера
            self.connection.connect((ip, port)) #и соответственно подключиться к порту и к ip сервера
            
            #ПОЛУЧАЕМ СВОЙ ЦВЕТ ОТ СЕРВЕРА
            data = self.connection.recv(1024) #data это данные, которые отправляет тебе клиент в виде байтов (максимум 1024 байтов)
            color_info = pickle.loads(data) #обратная выгрузка (получение значения цвета)
            self.am_i_white = (color_info["your_color"] == "white") #тут работает так, что self.am_i_white всегда false,
            #так как тебе хост отправляет инфу о том что ты черный. Тоесть, color_info["your_color"] == black по умолчанию. И "black == white = False"
            print(f"КЛИЕНТ: я {'белый' if self.am_i_white else 'черный'}") #сообщение об информации цветов (вообще клиент всегда черный)
            
            self.connected = True #ну и после этих манипуляций подключение началось
            threading.Thread(target=self._listen, daemon=True).start()#запуск фонового потока чтобы не зависнуть.
            #daemon = True это означает, что поток сам умрёт при закрытии программы
            self.opponent_connected.emit()
            self.status_message.emit("Подключено к игре!") #отправка сигнала о том что ты подключился
            return True
        except Exception as e: #обработчик исключений
            self.status_message.emit(f"Ошибка подключения: {e}") #или не смог подключиться
            return False

    def _accept_connection(self):
        try:
            self.connection, addr = self.server.accept() #получение подключения и адреса если сервер начал принимать подключения
            print(f"Подключение от {addr}")
            
            # Добавляем type
            color_data = pickle.dumps({"type": "color_info", "your_color": "black"}) #конвертация информации о цвете в байты
            self.connection.send(color_data) #отправка клиенту информации о его цвете
            
            self.connected = True #подключение успешно
            threading.Thread(target=self._listen, daemon=True).start() #уже объяснял
            self.opponent_connected.emit() 
            self.status_message.emit(f"Противник подключился!") #отправка сообщение хосту о том, что противник подключился
        except Exception as e:
            print(f"Ошибка при принятии: {e}") #если ошибка - доложить
                
    def _listen(self):
        """СЛУШАТЬ ВХОДЯЩИЕ СООБЩЕНИЯ"""
        
        print(f"Запуск слушателя для {'хост' if self.is_host else 'клиент'}") #чтобы было по красоте (сообщение которое просто показывает, клиент ты или хост)
        while self.connected: #пока подключен
            try:
                self.connection.settimeout(1.0) #таймаут ожидания данных
                data = self.connection.recv(1024) #получение байтов от противника
                if not data: #если нету байтов (соединение закрыто противоположной стороной), recv возвращает пустые данные. Это признак разрыва связи
                    print("Соединение закрыто")
                    break #выходим из цикла
                
                #проверка не служебное ли сообщение
                try:
                    msg = pickle.loads(data) # конвертация байтов в python объект (словарь или кортеж)
                    if isinstance(msg, dict) and 'type' in msg: # если это словарь с ключом 'type' то это служебное сообщение
                        if msg['type'] == 'color_info': #если тип сигнала - информация о цвете
                            print(f"Получена информация о цвете: {msg}")
                            continue
                        elif msg['type'] == 'resign': #если тип сигнала - информация о сдаче противника
                            print("Противник сдался")
                            self.resign_received.emit()
                            continue
                        elif msg['type'] == 'gamemode':
                            self.gamemode_received.emit(msg['gamemode'])
                        elif msg['type'] == 'rematch_request':
                            if self.is_my_request:
                                self.is_my_request = False
                                continue
                            self.rematch_request_received.emit()
                        elif msg['type'] == 'rematch_accept':
                            print("rematchaccept получен")
                            self.rematch_accept_received.emit()
                        elif msg['type'] == 'rematch_decline':
                            self.rematch_decline_received.emit()

                    else:
                        from_pos, to_pos = msg # Это не служебное сообщение, а ход!
                        print(f"Получен ход: {from_pos}→{to_pos}") #получение координатов
                        self.move_received.emit(from_pos, to_pos) #отправляем сигнал о позиции
                except:
                    pass
            except socket.timeout: #если за 1 секунду не пришли данные, то мы ловим исключение и продолжаем цикл, чтобы проверить,
                #не изменился ли статус self.connected
                continue
            except Exception as e:
                print(f"Ошибка при получении: {e}") #ну и если по какой то причине сигнал не дошел, то показываем ошибку
                break
        #если отключаемся то:
        print("Слушатель остановлен")
        self.connected = False
        self.opponent_disconnected.emit()
        
    def send_gamemode(self, gamemode):
        if self.connection and self.connected:
            try:
                data = pickle.dumps({"type": "gamemode", "gamemode": gamemode})
                self.connection.send(data)
                return True
            except:
                return False
        return False
    
    def send_rematch_request(self):
        if self.connection and self.connected:
            try:
                data = pickle.dumps({"type": "rematch_request"})
                self.connection.send(data)
                return True
            except:
                return False
        return False
    
    def send_rematch_accept(self):
        if self.connection and self.connected:
            try:
                self.is_my_request = True
                data = pickle.dumps({"type": "rematch_accept"})
                self.connection.send(data)
                return True
            except:
                return False
        return False
    
    def send_rematch_decline(self):
        if self.connection and self.connected:
            try:
                data = pickle.dumps({"type": "rematch_decline"})
                self.connection.send(data)
                return True
            except:
                return False
        return False

    def send_move(self, from_pos, to_pos):
        """ОТПРАВИТЬ ХОД"""
        if self.connection and self.connected: #если есть подключение и ты подключен
            try:
                data = pickle.dumps((from_pos, to_pos)) #конвертация объекта python в байты
                self.connection.send(data) #отправка противнику
                return True
            except Exception as e:
                print(f"Ошибка при отправке: {e}")
                self.connected = False #если соединение разорвалось то не отправляем
                return False
        return False
    
    def send_resign(self):
        """Отправить уведомление о сдаче"""
        if self.connection and self.connected: #если есть подключение и ты подключен
            try:
                data = pickle.dumps({"type": "resign"}) #конвертация объекта python в байты
                self.connection.send(data) #отправка противнику
                return True
            except Exception as e:
                print(f"Ошибка при отправке: {e}")
                self.connected = False #если соединение разорвалось то не отправляем
        return False
                   
    def disconnect(self):
        """Отключение от сети"""
        self.connected = False #логично, что соединение пропадет, то есть ты будешь не подключен
        if self.connection: #если есть подключение
            try:
                self.connection.close() #закрыть соединение
            except: 
                pass #если его нет то закрывать нечего
        if self.server: 
            try:
                self.server.close()
            except:
                pass #то же самое и с сервером
            
    def get_local_ip(self):
        """УЗНАТЬ СВОЙ IP В ЛОКАЛЬНОЙ СЕТИ"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #назначаем протокол для отправки пакета, чтобы узнать свой ip - IPv4 + UDP
            s.connect(("8.8.8.8", 80)) #8,8,8,8 - публичный dns-сервер гугл. он заставляет систему выбрать сетевой интерфейс, через который мы входим в гугл
            #вообще соединение полностью не устанавливается (udp не соединяется), но ОС запоминает, через какой интерфейс пройдет трафик
            ip = s.getsockname()[0] #функция о получении локального адреса сокета
            s.close() #ну и закрываем временный сервер
            return ip #вернуть айпи
        except:
            return "127.0.0.1" #вернуть это значение если не получилось
        
    def is_connected(self):
        return self.connected #ну и вспомогательная функция о том что кто то подключен