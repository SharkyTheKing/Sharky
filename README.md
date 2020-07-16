# Sharky
Codes that I've been working on for use, feedback and issues are welcomed!

## Install
These codes are for [Red Discord Bot](https://github.com/Cog-Creators/Red-DiscordBot), you MUST have a up-todate RedBot to use and/or install these codes. 

## Announcements
Announcements Cog. Announcing a message in a channel while pinging a singular role through the bot.

Three commands:
- Alert: Optional to mention a role, if no channel is given it'll default to current channel. This lets you send a message in your selected channel. It'll ping a role if one was given.
- MessageEdit: Edits the message by the bot.
- Mentionable: Lets you make a role mentionable or not.

## Charlimit
Limits amount of characters and lines your members are able to send in a channel.

This works perfect for LFG channels that you want to limit the amount of spam they put into their messages.

It'll also send a message saying how many characters / lines is needed to not be removed, though this is defauled to being off. You must turn this on to allow for it to send a message. Currently, not adjustable message. 

## Lockdown
Lockdown system for guilds. Let's you completely lockdown your server Text Channels with having the option for the bot to leave a message.

> Note: You MUST have set the proper permissions for the bot to be able to send_messages and manage_channels in each of the channels affected or else this could cause issues.

Commands:
- Lockdown: Does fullscale lockdown, with asking for permission before doing so.
- Unlockdown: Does fullscale unlockdown, asks permission before doing so.
- ChannelLock: Locks down a single channel that you select, Text or Voice channel.
- ChannelUnlock: Unlocks a single channel that you select.
- Lockdownset Lockmsg: Gives the bot a message to put in the channels if the Lockdown command is thrown.
- Lockdownset Unlockmsg: Gives the bot a message to put in channels if the UnLockdown comand is thrown.

## NewsPublish
Automatic news publishing for verified / partnered servers that have a news channel.

> Note: The bot must have manage_messages permissions to publish your messages.

This lets you automatically publish messages via bot, in your news channels. You can set an alert message so the bot will alert the selected channel if it's unable to publish the new message due to Discord's Ratelimit of publishing.

Commands:
- Addnews: Adds the news channel, checks if the channel is a news channel and checks permissions
- RemoveNews: Removes the selected channels from listing
- AlertChannel: Sets the alertchannel to notify if publish failed.

