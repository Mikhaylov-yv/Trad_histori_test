from datetime import datetime
# from open_fnam_data import open
import pandas as pd

class Financial_account:

    def __init__(self):
        # Количество свободных денег
        self.free_money = 0
        # Купленные акции и их количество
        self.tool_dict = {}
        # Дата и время
        self.val_portfel = 0
        # Изменение размера портфеля


    def add_mone(self, amount_of_money):
        self.free_money = self.free_money + amount_of_money
        # self.portfel_price = self.get_portfel_price()

    # Метод для покупки акций
    def buy_lot(self,lot_name, lot_count,lot_size, lot_price, commission = 0.00015):
        commission = commission * lot_count * lot_price * lot_size
        if self.free_money <= lot_count * lot_price + commission:
            return print('Ограниечение по деньгам')
        if lot_name in self.tool_dict:
            self.tool_dict[lot_name] += lot_count
        else:
            self.tool_dict[lot_name] = lot_count * lot_size
        self.free_money -= lot_price * lot_count * lot_size + commission
        # self.portfel_price = self.get_portfel_price()

    #  Метод для продажи акций
    def sell_lot(self, lot_name, lot_count, lot_size, lot_price, commission=0.00015):
        commission = commission * lot_count * lot_price * lot_size
        if lot_name not in self.tool_dict: return print('Лоты отсутствуют')
        if self.tool_dict[lot_name] < lot_count: return print('Ограничение по количеству лотов')
        self.tool_dict[lot_name] -= lot_count * lot_size
        self.free_money += lot_price * lot_count * lot_size  + commission
        # self.portfel_price = self.get_portfel_price()

    # Определяем стоимость портфеля
    def get_portfel_price(self, cot_dict, commission=0.00015):

        val_mani_in_lot = 0
        for tool in list(cot_dict):
            if tool not in list(self.tool_dict): continue
            vol = self.tool_dict[tool]
            prise = cot_dict[tool]
            commission = vol * prise * commission
            val_mani_in_lot += vol * prise - commission
        self.val_portfel = self.free_money + val_mani_in_lot
        return self.val_portfel



if __name__ == '__main__':
    ak = Financial_account()
    ak.add_mone(10000)
    ak.buy_lot(lot_name='HYDR', lot_count=10, lot_size=1000, lot_price=0.567)
    ak.get_portfel_price({'HYDR': 0.7})
    # {'HYDR': 0, 'YNDX': 0}
    print(ak.__dict__)

    # ak.buy_lot('YNDX',2,568.54,3)
    # print(ak.free_money, ak.tool_dict)
    # ak.sell_lot('YNDX', 2, 600)
    # print(ak.free_money, ak.tool_dict)