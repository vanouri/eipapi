from dataGetteur import DataSetManager
from technicalData import libHandler
from P2PCore import P2P
import argparse
from dotenv import load_dotenv
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning) 
warnings.simplefilter(action='ignore', category=RuntimeWarning) 
load_dotenv()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("-p", help="give you the next Forcast" ,action='store_true')
group.add_argument("-f", help="give you and play the next Forcast" ,action='store_true')

arg = parser.parse_args()

if (arg.f == True):
    core = P2P(60, False)
    core.forcast()

if (arg.p == True):
    core = P2P()
    core.print_forcast()
