import logging

# logging config
logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s: ' \
                    '%(message)s',
                    datefmt='%d/%b/%Y %H:%M:%S',
                    level=logging.DEBUG,
                    filemode='w',
                    filename='gx_communication.log')
