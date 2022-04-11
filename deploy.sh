git pull
kill $(ps -ef | grep chiyakbot.py | gawk '/python3/ { print $2 }')
sleep 5
nohup python3 -u chiyakbot.py production > chiyakbot.log &