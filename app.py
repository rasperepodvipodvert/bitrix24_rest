from bitrix24_python import Bitrix24

bx24 = Bitrix24('sysadmin.bitrix24.ru', '5hi9bb2vqmqql3sr')
print(bx24.call('app.info'))