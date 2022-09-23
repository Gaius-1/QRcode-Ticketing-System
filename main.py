from config import *
from webserver import *
import sys

guests = [{"name": "Claudia", "phone_number": "0245470502", "status": "SINGLE TICKET"},
          {"name": "Sammy", "phone_number": "0557491888", "status": "SINGLE TICKET"},
          {"name": "Jennifer Bour", "phone_number": "0549762924", "status": "SINGLE TICKET"},
          {"name": "Gabby", "phone_number": "0554567060", "status": "SINGLE TICKET"},
          {"name": "Matilda", "phone_number": "0552972804", "status": "SINGLE TICKET"},
          {"name": "Marvina", "phone_number": "0501352332", "status": "SINGLE TICKET"},
          {"name": "Collins", "phone_number": "0549224512", "status": "SINGLE TICKET"},
          {"name": "William & Jessica", "phone_number": "0591910642", "status": "COUPLE TICKET"},
          {"name": "Kyei Mensah & Comfort", "phone_number": "0554501944", "status": "COUPLE TICKET"},
          {"name": "Keziah, Tracy, Joshua and Kelvin", "phone_number": "0204557417", "status": "DOUBLE TICKET"}
         ]

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'

    if command == 'generate_ticket_link':
        agree = input('This will create a new file. Are you sure? (y/n) ')
        if agree == 'y':
            from excel_handler import generate_ticket_link
            generate_ticket_link(INPUT_FILE_PATH, OUTPUT_FILE_PATH, DOMAIN_NAME)
            from webserver import get_nginx_config
            get_nginx_config()

    elif command == 'run_webserver':
        # from webserver import run_server
        run_server()

    elif command == 'add_guests':
        from excel_handler import add_new_guest_from_excel
        add_new_guest_from_excel(OUTPUT_FILE_PATH, guests, DOMAIN_NAME)

    elif command == 'help':
        print('Available commands:')
        print('\tadd_guests')
        print('\trun_webserver')
        print('\thelp')
