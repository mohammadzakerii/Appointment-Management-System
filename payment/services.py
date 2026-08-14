import requests
from django.conf import settings
from rest_framework import serializers

class ZarinPalService:
    BASE_URL = 'https://sandbox.zarinpal.com/pg/v4/payment'
    REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    START_PAY_URL = "https://sandbox.zarinpal.com/pg/StartPay/"

    def __init__(self):
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID

    def create_payment(self, * , amount, description, callback_url, mobile=None, email=None):
        payload = {
            "merchant_id":self.merchant_id,
            "amount":int(amount),
            "callback_url": callback_url,
            "description": description
        }

        metadata = {}
        if mobile:
            metadata["mobile"] = mobile

        if email:
            metadata["email"] = email

        if metadata :
            payload["metadata"] = metadata        

        response = requests.post(self.REQUEST_URL, json=payload, timeout=10)

        print("STATUS:",response.status_code)
        print("TEXT:", response.text)
        print("HEADERS:", response.headers)

        response.raise_for_status()
        data = response.json()
        if data["data"]["code"] != 100:
            raise Exception(data["data"]["errors"])
        authority = data["data"]["authority"]

        return {
            "authority":authority,
            "payment_url": f"{self.START_PAY_URL}{authority}"
        }

    def verify_payment(self, amount, authority):
        print(self.merchant_id)
        payload = {
            "authority":authority,
            "merchant_id":self.merchant_id,
            "amount":int(amount)
        }   
        response = requests.post(self.VERIFY_URL, json=payload, timeout=10)

        response.raise_for_status()

        data = response.json()
        print(data)
        if data["data"]["code"] not in [100,101]:
            raise serializers.ValidationError(data["errors"])

        return {
            "ref_id": data["data"]["ref_id"],
            "code": data["data"]["code"],
            "card_num":data["data"]["card_pan"],
            "message": data["data"]["message"]
        }  

          