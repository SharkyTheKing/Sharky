# Sharky
Codes that I've been working on for use, feedback and issues are welcomed!

## Where to find me
[Red Cog Support](https://discord.gg/GET4DVk)

## Install
These codes are for [Red Discord Bot](https://github.com/Cog-Creators/Red-DiscordBot), you MUST have a up-todate RedBot to use and/or install these codes.

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

## MailSystem
> Warning: This is a pre-release, this is not close to being completed, I need more feedback and information from Red users.
> This means that by installing this cog, you understand there is a risk that issues could happen for you, your bot, or the members using your bot.

I am still working on this cog and thinking of ways to handle different things. Currently, this doesn't support restricting modmail to a specific guild. By installing you are allowing every guild owner (or staff that is considered an admin or has manage_channel permissions) the ability to set this up for their guild.

Do not submit random PRs without talking to me or Kreusada, the code is set the way it is for future plans that I won't discuss publicly yet.

> Note: These are subject to change at any moment's notice due to the pre-release.

Commands:
- DmMail: DM command - Starts the process to send a mail ticket to chosen server.
- StopMail: DM command - Not finished.

- Mailset: Default command group for Mailsystem Settings
- Mailset Activate: Sets the system to be enabled or disabled.
    - Must have the category set first, otherwise won't be activated.
- Mailset Category: Sets the category that channels will be created in.
- Mailset Commands: Not finished.
- Mailset Embeds: Not finished.
- Mailset LogChannel: Sets the logging channel for when a modmail has been created or closed.
- Mailset ShowSettings: Shows the guild's current settings.

## MorseShark
Allows you to encode string into morsecode and lets you decode morsecode into text. Currently only English's standard text is available, if you'd like to help allow for more customizability, please reach out through the red's cog support server.

This is just a simple morse code cog, if you want to take from this cog and use it in your own example, please feel free to.

> Note: This can be spammy, as it accounts for users who have 4k character limit.

Commands:
- Morse: Default command group
- Morse Encode: Encode a string into morse code.
- Morse Decode: Decodes morse code text into readable text.

## MsgTracker
Counts how many messages a person sends in the guild if enabled. Sorts them into a leaderboard to display, allows for the members to set themselves to be ignored from the bot. Staff members have to allow them to be tracked if the member changes their mind.

> Note: As a bot owner, you have the ability to disable the command that sets members to be ignored. This is up to you, though this Cog will still handle data deletions regardless of the command setting.

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
- ReportDM: Toggle whether to be DMed when you report.
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

## Verify
Server verification system, requires people to type command to be allowed access in server

> Note: This requires your knowledge of locking people out via role. This does not automatically handle this, it assumes you are or the person using this is capable of setting Discord permissions to disallow member viewing any channel except Rules and whatever channel used to send the command in.
> Due to this, this requires Manage_Roles
