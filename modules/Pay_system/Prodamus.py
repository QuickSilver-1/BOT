#import Pay_system
from requests import get
from hmac import new
from hashlib import sha256

#                        order_id, price, quantity, name, 
#                        customer_extra="", customer_number="", customer_email="", tax="", 
#                        tax_type="", subscription_id="", urlReturn="", urlSuccess="", 
#                        discount_value="", subscription_date_start=""

class Prodamus():

    def __init__(self, url, key):
        self.PAY_URL = url
        self.SECRET_KEY = key

class Order:
    
    def __init__(self, connection, products, data) -> None:
        true_data = self.__successful_data(data)
        true_products = self.__successful_products(products)
        if true_data[0] and true_products[0]:
            self.URL = self.__create_order_url(connection, products, data)

        elif not(true_data[0]):
            raise true_data[1]
        
        else:
            raise true_products[1]

    def create_pay_link(self) -> str:
        request = get(self.URL)
        if request.status_code == 200:
            return request.text
        else:
            raise ConnectionError(f"Server error {request.status_code}")
        
    def get_sign(self) -> str:
        try:
            return self.sign
        except:
            raise KeyError("Sign еще не сформирован")

    def __create_order_url(self, connection, products, data) -> None:
        products_url = "?" + "&".join([f"products[0][{i}]={products[i]}" for i in products])
        data_url = "&" + "&".join([f"{i}={data[i]}" for i in data])
        self.__create_signature(connection, data, products)
        return f"https://{connection.PAY_URL}/" + products_url + data_url + "&do=link" + f"&singature={self.sign}"


    def __successful_products(self, products) -> TypeError:
        
        true_products = {
            "price": [str, int],
            "quantity": [str, int],
            "name": [str]
        }
        for i in true_products:
            if i not in products:
                return False, TypeError(f"Not found {i} for order")
            
            if type(products[i]) not in true_products[i]:
                return False, TypeError(f"Not correct type for {i}")
            
            return True, None

    def __successful_data(self, data) -> TypeError:
        return True, None

    def __create_signature(self, connection, data, products):
        data.update(products)
        self.sign = new(connection.SECRET_KEY.encode(), str(data).encode() , sha256).hexdigest()
