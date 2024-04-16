import aiohttp
import asyncio
import sys
import json
from datetime import datetime, timedelta


class APIFetcher:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    @staticmethod
    async def fetch_data(date):
        async with aiohttp.ClientSession() as session:
            async with session.get(APIFetcher.BASE_URL + date) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    @staticmethod
    async def fetch_exchange_rates(dates):
        tasks = [APIFetcher.fetch_data(date) for date in dates]
        return await asyncio.gather(*tasks)


class DataProcessor:
    @staticmethod
    def process_data(data):
        rates = []
        for item in data:
            date_str = item['date']
            eur_rate = next((rate for rate in item['exchangeRate'] if rate['currency'] == 'EUR'), None)
            usd_rate = next((rate for rate in item['exchangeRate'] if rate['currency'] == 'USD'), None)
            
            if eur_rate and usd_rate:
                rates.append({
                    date_str: {
                        'EUR': {
                            'sale': eur_rate['saleRateNB'],
                            'purchase': eur_rate['purchaseRateNB']
                        },
                        'USD': {
                            'sale': usd_rate['saleRateNB'],
                            'purchase': usd_rate['purchaseRateNB']
                        }
                    }
                })
        return rates


class ConsolePrinter:
    @staticmethod
    def print_rates(rates):
        print(json.dumps(rates, indent=2))


async def main(days):
    dates = [(datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days + 1)]
    
    try:
        data = await APIFetcher.fetch_exchange_rates(dates)
        rates = DataProcessor.process_data(data)
        ConsolePrinter.print_rates(rates)
    except aiohttp.ClientError as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: py .\\main.py <number_of_days>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        if days > 10:
            print("You can fetch rates for up to 10 days only.")
            sys.exit(1)
    except ValueError:
        print("Invalid number of days.")
        sys.exit(1)

    asyncio.run(main(days))
