from schedule import every, run_pending
from bot import new_day


def main():
    every().day.at("09:00").do(new_day)
    while True:
        run_pending()

if __name__ =="__main__":
    main()