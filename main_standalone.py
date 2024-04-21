import asyncio
from airtouch4pyapi import AirTouch
import logging
import os
from datetime import datetime
import threading

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set up logging
log_folder = os.path.join(script_dir, "logs")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    
log_file = os.path.join(log_folder, f"aircon_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def updateInfoAndDisplay(ip):
    try:
        # Connect to AirTouch device
        at = AirTouch(ip)
        await at.UpdateInfo()
        acs = at.GetAcs()
        groups = at.GetGroups()

        # Identify main bedroom (we won't manage other rooms)
        room = next((group for group in groups if group.GroupName == "Main Bed"), None)

        # Calculate correct fan open ratio
        flooms_open_ratio = (room.Temperature - 22.8)
        flooms_open_ratio = max(flooms_open_ratio, 0.05)
        flooms_open_ratio = min(flooms_open_ratio, 1)
        flooms_open_ratio = flooms_open_ratio * 100
        flooms_open_ratio = round(flooms_open_ratio)

        if flooms_open_ratio == 5:
            await at.TurnAcOff(0)
            logging.info("Turning AC off")
        else:
            if acs[0].IsOn == "Off":
                await at.TurnAcOn(0)
                logging.info("Turning AC on")

        # Update room temperature
        await at.SetGroupToTemperatureByGroupName(room.GroupName, 23)
        await at.SetGroupToPercentByGroupName(room.GroupName, flooms_open_ratio)

        logging.info(f"Room Temperature: {room.Temperature}")
        logging.info(f"Fan Open Ratio: {flooms_open_ratio}")
        logging.info(f"AC Status: {acs[0].IsOn}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

async def main():
    while True:
        try:
            await updateInfoAndDisplay("192.168.50.20")
            logging.info("Waiting for 5 minutes...")
            await asyncio.sleep(300)  # Sleep for 5 minutes (300 seconds)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            logging.info("Retrying in 1 minute...")
            await asyncio.sleep(60)  # Sleep for 1 minute before retrying

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

def run_in_thread():
    thread = threading.Thread(target=run)
    thread.start()

if __name__ == '__main__':
    run_in_thread()