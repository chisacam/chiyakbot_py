git pull
kill $(ps -ef | grep chiyakbot.bot | gawk '/python/ { print $2 }')
sleep 10
nohup python -m chiyakbot.bot production > chiyakbot.log &