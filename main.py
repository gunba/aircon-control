import logging
import os
from datetime import datetime
import asyncio
from airtouch4pyapi import AirTouch

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

        # Lower the target temperature by 0.5 degrees
        target_temperature = 22.5

        # Calculate correct fan open ratio based on the new target temperature
        flooms_open_ratio = (room.Temperature - target_temperature)
        flooms_open_ratio = max(flooms_open_ratio, 0.05)
        flooms_open_ratio = min(flooms_open_ratio, 1)
        flooms_open_ratio = flooms_open_ratio * 100
        flooms_open_ratio = round(flooms_open_ratio)

        if flooms_open_ratio < 20:
            await at.TurnAcOff(0)
            logging.info(f"Turning AC off. Current Room Temperature: {room.Temperature}")
        else:
            if acs[0].IsOn == "Off":
                await at.TurnAcOn(0)
                logging.info("Turning AC on")
            # Update room temperature and fan open ratio
            await at.SetGroupToTemperatureByGroupName(room.GroupName, target_temperature)
            await at.SetGroupToPercentByGroupName(room.GroupName, flooms_open_ratio)
            logging.info(f"Room Temperature: {room.Temperature}")
            logging.info(f"Fan Open Ratio: {flooms_open_ratio}")
            logging.info(f"AC Status: {acs[0].IsOn}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

def run(ip):
    asyncio.run(updateInfoAndDisplay(ip))

if __name__ == '__main__':
    run("192.168.50.20")
