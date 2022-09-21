from config import *
from webserver import *
import sys

guests = [{"name": "Wendy", "phone_number": "0552354449", "status": "SINGLE TICKET"},
          {"name": "Dzramado E.", "phone_number": "0247622263", "status": "SINGLE TICKET"},
          {"name": "Barbara", "phone_number": "0545873989", "status": "SINGLE TICKET"},
          {"name": "Dzifa", "phone_number": "0559586391", "status": "SINGLE TICKET"},
          {"name": "Armando & Bae", "phone_number": "0594764182", "status": "COUPLE TICKET"}]

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
