git pull
kill $(ps -ef | grep chiyakbot.bot | awk '/python/ { print $2 }')
sleep 10
python setup.py build
nohup python -m chiyakbot.bot production > chiyakbot.log &