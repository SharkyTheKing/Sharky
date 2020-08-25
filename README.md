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

> Note: This needs send_mesage at least, to send the messages to the specific channels.

## Charlimit
Limits amount of characters and lines your members are able to send in a channel.

This works perfect for LFG channels that you want to limit the amount of spam they put into their messages.

It'll also send a message saying how many characters / lines is needed to not be removed, though this is defauled to being off. You must turn this on to allow for it to send a message. Currently, not adjustable message. 

> Note: You MUST have set the proper permissions for the bot to be able to manage_messages in each of the channels affected or else this could cause issues.

## Lockdown
Lockdown system for guilds. Let's you completely lockdown your server Text Channels with having the option for the bot to leave a message.

> Note: You MUST have set the proper permissions for the bot to be able to send_messages, manage_channels, manage_permissions in each of the channels affected or else this could cause issues.

Commands:
- Lockdown: Does fullscale lockdown, with asking for permission before doing so.
- Unlockdown: Does fullscale unlockdown, asks permission before doing so.
- ChannelLock: Locks down a single channel that you select, Text or Voice channel.
- ChannelUnlock: Unlocks a single channel that you select.
- Lockdownset Lockmsg: Gives the bot a message to put in the channels if the Lockdown command is thrown.
- Lockdownset Unlockmsg: Gives the bot a message to put in channels if the UnLockdown comand is thrown.

## NameGen
Gives a random name based on first name and last name lists created by you.

> Note: There are two functionality. Either sending a message or renaming someone when using the primary command. If you want it to rename, then the bot must need manage_nicknames permission

Commands:
- NameSet List: Displays your lists of names and settings.
- NameSet Rename: Toggle system to either rename or send message.
- NameSet GenMessage: Let's you customize the response when the bot gives/changes name.
- NameSet Add FirstName: Adds your first names to list.
- NameSet Add LastName: Adds your last names to list.
- NameSet Remove FirstName: Removes your first names from list.
- NameSet Remove LastName: Removes your last names from list.
- NameGen: Generate a random name and outputs either via text or by changing your name.

## NewsPublish
Automatic news publishing for verified / partnered servers that have a news channel.

> Note: The bot must have manage_messages and send_messages permissions to publish your messages.

This lets you automatically publish messages via bot, in your news channels. You can set an alert message so the bot will alert the selected channel if it's unable to publish the new message due to Discord's Ratelimit of publishing.

Commands:
- Addnews: Adds the news channel, checks if the channel is a news channel and checks permissions
- RemoveNews: Removes the selected channels from listing
- AlertChannel: Sets the alertchannel to notify if publish failed.

## Reports
Report system for Moderators of servers.

> Note: The bot must have send_messages and manage_messages permissions or else this could cause issues.

This is a simple report members cog, you set it up and members can report members to the server's moderator without having to have hassles of contacting a moderator directly.

Commands:
- Report: Reports a member, sends to selected channel in server for moderator's preview.
- ReportSet Channel: Sets the channel reports goes into.
- ReportSet Emotes: Sets if the bot automatically adds emotes to the reports sent.

## SharkyTools
Tools that I've made for personal use.

> Note: If you are to use this, this needs ban_members permissions for the `findban` command.

Shows members account information (join date, profile picture, etc). Can show specific's users avatar. Find if someone's banned based off of userid.

Commands:
- Uav: Allows you to preview a user's avatar. (Must be userid)
- Avatar: Shows member's avatar (Note: Can cause conflict with other cogs for same command)
- Age: Shows member's age (Join date, account creation, etc)

## StrawPoll
Create polls through StrawPoll's API!

Allows members to make a poll through StrawPoll. Returns a link to the poll after questionaire is finished. This allows for one member per guild active at a time so it doesn't get spammed on the bot.

## Verify
Server verification system, requires people to type command to be allowed access in server

> Note: This requires your knowledge of locking people out via role. This does not automatically handle this, it assumes you are or the person using this is capable of setting Discord permissions to disallow member viewing any channel except Rules and whatever channel used to send the command in.
> Due to this, this requires Manage_Roles

