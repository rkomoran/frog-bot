## Froggo's Daily Facts

*Ever wanted your daily facts presented by a frog in English and Froglish? Well, you're in luck!*


>***Enhance your Discord server with this bot that delivers random daily facts to a channel of your choice using /setchannel. Adding a whimsical twist, each fact is presented by a frog, complete with a random frog image and a unique translation in Froglish.***


![frogbot_recording(5)](https://github.com/user-attachments/assets/4930ef2b-2e35-4cda-8456-b7e4281af2ce)


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

### Hosting on AWS EC2
To ensure the bot runs 24/7, it is hosted on an AWS EC2 instance. The bot is set up to restart automatically and handle any downtime efficiently, ensuring it is always available to deliver your daily facts by a froggo.

### Top.gg Page
Check out Froggo's Daily Facts bot on [top.gg](https://top.gg/bot/1263169512807596137) for more details and to invite the bot to your server!
