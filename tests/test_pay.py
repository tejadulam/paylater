from unittest import TestCase, main
import json
import requests

class TestCases(TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def test_new_user(self):

        url = "http://127.0.0.1:8000/newUser"

        payload = json.dumps({
        "name": "Teja",
        "email": "teja@gmail.com",
        "balance": 1200
        })

        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()
        
        self.assertEqual(response["status"], "success")
   
    def test_new_merchant(self):
    
        url = "http://127.0.0.1:8000/newMerchant"

        payload = json.dumps({
        "name": "pizza",
        "email": "pizza@gmail.com",
        "fee": 300
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"], "success")


    def test_transact(self):
        url = "http://127.0.0.1:8000/transact"

        payload = json.dumps({
        "u_id": 1,
        "m_id": 3,
        "amount": 500
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"], "success")


    def test_get_merchant(self):
        url = "http://127.0.0.1:8000/getMerchant/3"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"],"success")


    def test_update_fee(self):
        url = "http://127.0.0.1:8000/updateFee?mid=1&fee=200"

        payload = {}
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"],"success")


    def test_repay(self):
        url = "http://127.0.0.1:8000/repay?name=James&amount=300"

        payload = {}
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload)
        self.assertEqual(response["status"],"success")


    def test_fee(self):
        url = "http://127.0.0.1:8000/fee/Blinkit"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"],"success")


    def test_dues(self):
        url = "http://127.0.0.1:8000/dues/James"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"],"success")



    def test_userlimit(self):
        url = "http://127.0.0.1:8000/usersAtLimit"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"],"success")
        


    def test_totalDues(self):
        url = "http://127.0.0.1:8000/totalDues"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()
        self.assertEqual(response["status"],"success")
            
            
if __name__ == '__main__':
    main()