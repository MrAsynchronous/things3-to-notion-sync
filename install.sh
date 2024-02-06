launchctl unload ~/Library/LaunchAgents/com.brandonwilcox.thingstonotionsync.plist
yes | cp dist/main /Users/brandonwilcox/thingstonotionsync
launchctl list | grep com.brandonwilcox.thingstonotionsync