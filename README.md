# Zabbix Traffic Light

<a href="https://www.cleware-shop.de/USB-MiniTrafficLight">
<img src="https://github.com/niceshops/zabbix-ampel/blob/main/vendor/ampel.png" alt="Ampel" width="400"/>
</a>

## Setup

1. Buy a USB traffic light - in our case we used [this one](https://www.cleware-shop.de/epages/63698188.sf/en_GB/?ViewObjectPath=%2FShops%2F63698188%2FProducts%2F41%2FSubProducts%2F41-1)
2. Install a host-system to trigger the traffic-light - in our case we needed an x86-bit linux/raspbian as [the cli-binary](https://github.com/niceshops/zabbix-ampel/blob/main/vendor/USBswitchCMD.zip) only supported that architecture
3. Make sure you can trigger its lights manually using the shell
4. Make sure the host-system can access the Zabbix Server web-interface (_firewalling_)
5. Create an API user

  * See: [Zabbix Docs](https://www.zabbix.com/documentation/current/en/manual/config/users_and_usergroups/user)
  * You may need to create a custom user-role: [Zabbix Docs](https://www.zabbix.com/documentation/current/en/manual/config/users_and_usergroups/permissions#user-roles)
  * Groups: Readers
  * Permissions: 

    * User-type: User
    * Permissions: Read access on groups you want to 'display'

6. Copy the script to the host-system and update/modify the variables as needed:

  * API_URL, API_USER, API_PWD
  * AMPEL_CMD => path to your executable
  * CHOICES => map the zabbix trigger priority to commands

7Install the requirements

  ```bash
  python3 -m pip install pyzabbix
  ```

8. Add a service to run the script

  ```bash
  cp ampel.service /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable ampel.service
  systemctl start ampel.service
  systemctl status ampel.service
  ```
