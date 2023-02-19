git pull
kill $(ps -ef | grep chiyakbot.py | gawk '/python3/ { print $2 }')
sleep 5
nohup python -m chiyakbot.bot production > chiyakbot.log &