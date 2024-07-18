## Froggo's Daily Facts

*Ever wanted your daily facts presented by a frog in English and Froglish? Well, you're in luck!*


>***Enhance your Discord server with this bot that delivers random daily facts to a channel of your choice using /setchannel. Adding a whimsical twist, each fact is presented by a frog, complete with a random frog image and a unique translation in Froglish.***


![frogbot_recording(5)](https://github.com/user-attachments/assets/4930ef2b-2e35-4cda-8456-b7e4281af2ce)

### Top.gg Page
Check out Froggo's Daily Facts bot on [top.gg](https://top.gg/bot/1263169512807596137) for more details and to invite the bot to your server!

## How was this bot made?

Froggo's Daily Facts bot was crafted using Python and the [discord.py](https://discordpy.readthedocs.io/en/stable/) library. The bot's functionality revolves around delivering random facts with a fun twist. Here's a breakdown of the key components:

### Bot Setup and Event Handling
The bot initializes with all intents enabled, ensuring it can interact fully with the server's events and messages. It also ensures that commands are synced across all guilds the bot is part of.

### Frog Bot Commands
- **/setchannel**: Users can set a specific channel to receive daily frog facts.
- **/speak**: The bot outputs a random frog-related quote.
- **/fact**: Fetches a random fact along with its translation in Froglish.
- **/frogpic**: Returns a random frog picture.
- **/sync**: Syncs slash commands for the current guild, accessible only by the bot owner.

*This bot also reacts with a 🐸 emoji to a message that contains the word 'frog'*

### Daily Fact Delivery
A daily task runs every 24 hours, delivering a fact and a frog picture to the designated channel. This uses the `tasks.loop` decorator from `discord.ext`.

### Fetching Random Facts and Frog Pictures
- **Random Facts**: The bot fetches random facts from the [uselessfacts API](https://uselessfacts.jsph.pl/).
- **Frog Pictures**: It scrapes random frog images from [All About Frogs](http://allaboutfrogs.org/funstuff/randomfrog.html) using BeautifulSoup and aiohttp for asynchronous HTTP requests.

## Hosting on AWS EC2
To ensure the bot runs 24/7, it is hosted on an AWS EC2 instance. The bot is set up to restart automatically and handle any downtime efficiently, ensuring it is always available to deliver your daily facts by a froggo.

### Enabling and Starting the Service

After setting up the bot, I had to figure out a way to make it run continously. I used a systemd service on an AWS EC2 instance. Here's how I went about doing it:

- Made the service file in the corresponding folder

```bash
sudo nano /etc/systemd/system/discordbot.service
```

```ini
[Unit]
Description=Discord Bot Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user
ExecStart=/usr/bin/python3 /home/ec2-user/frogbot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

- Then, I did the following to start the service, and ensure it works:
  - Reload systemd
    
    ```bash
    sudo systemctl daemon-reload
    ```
  - Enable the service to start on boot

    ```bash
    sudo systemctl enable discordbot.service
    ```

  - Start it

    ```bash
    sudo systemctl start discordbot.service
    ```

  - I then checked it if was active, and saw something like this -- which ensured it was working:
  
    ```bash
    ● discordbot.service - Discord Bot Service
    Loaded: loaded (/etc/systemd/system/discordbot.service; enabled; vendor preset: enabled)
    Active: active (running) since ...
    Main PID: ...
    Tasks: ...
    Memory: ...
    CPU: ...
    CGroup: /system.slice/discordbot.service
            └─...
    
    ... more details ...
    ```
    
  That's pretty much it! To stop it, I would do this:

  ```bash
  sudo systemctl stop discordbot.service
  ```

  ```bash
  sudo systemctl disable discordbot.service
  ```

  ```bash
  sudo systemctl status discordbot.service
  ```


## Froggo's Daily Facts : What I Learned

>Building Froggo's Daily Facts was a blast!  It totally levelled up my coding skills in a bunch of areas:

- *APIs:* Who knew you could grab random facts from the internet? Using something called a "uselessfacts API" (seriously, that's the name!), I learned how to snag info from other programs and make Froggo even smarter; like parsing JSON responses to fetch some frog pictures. Plus, figuring out how to translate that info into code and deal with any hiccups was a fun challenge.

- *Corooutines & Asynchronous Programming:* This sounds fancy, but basically it lets Froggo fetch froggy pictures without getting stuck. Imagine juggling - you can keep an eye on all the balls (requests) without dropping any. This keeps Froggo nice and responsive for everyone. Thanks to aiohttp and discord.py for making this possible!
  
- *AWS Hosting:* Taking Froggo from my computer to the cloud with AWS EC2 was like moving to a bigger pond. I learned how to set everything up, keep Froggo running smoothly, and fix any bumps along the road.

Overall, Froggo Facts wasn't just fun for you guys, it was a major learning experience for me.  Now I can build even cooler bots for everyone to enjoy!
