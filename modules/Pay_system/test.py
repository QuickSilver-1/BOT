from Prodamus import Prodamus, Order

connection = Prodamus("Bredis.payform.ru", "123")
test_pay =  Order(connection, {"name": "Тестовая оплата", "price": 100, "quantity": 1}, {"customer_extra": "Это тестовая ссылка", "order_id": 666})

print(test_pay.create_pay_link())



