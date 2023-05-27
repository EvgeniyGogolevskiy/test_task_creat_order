import pytest
from create_order_binance import validate_data, main

test_data = {
    "symbol": 'ETHUSDT',
    "api_key": 'r7naGWVGWE09UKanEFymSRh7mjqlxPI7H2a6TLDKM2MUaYjbx81siwdh0iF0IRiY',
    "secret_key": 'pP0Ak9TFKEEMpGUZA0k839u7rwVASD1xoHY3kfczUlHG1HJBEMry4LtkaaYSziyB'
}


def test_validate_data():
    assert validate_data({}) == False
    assert validate_data({"volume": 10000.0,
                          "number": 5,
                          "amountDif": 50.0,
                          "side": "SELL",
                          "priceMin": 200.0,
                          "priceMax": 300.0}) == True
    assert validate_data({"volume": 10000.0,
                          "number": 5,
                          "amountDif": 50.0,
                          "side": "BUY",
                          "priceMin": 200.0}) == False


def test_create_orders():
    with pytest.raises(Exception):
        main({"side": "BUY"}, test_data)

    # Test for creating buy orders
    main({"volume": 300.0,
           "number": 3,
           "amountDif": 50.0,
           "side": "BUY",
           "priceMin": 1700.0,
           "priceMax": 1900.0}, test_data)
    # Test for creating sell orders
    main({"volume": 300.0,
           "number": 3,
           "amountDif": 50.0,
           "side": "SELL",
           "priceMin": 1700.0,
           "priceMax": 1900.0}, test_data)