from BX24 import Bitrix24
import json

bx24 = Bitrix24('sysadmin', '5hi9bb2vqmqql3sr')

# print(json.dumps(bx24.call('tasks.task.list'), indent=4, sort_keys=True))
data = {
    'fields': {
        "TITLE": "ИП Титов",
        "NAME": "Глеб",
        "SECOND_NAME": "Егорович",
        "LAST_NAME": "Титов",
        "STATUS_ID": "NEW",
        "OPENED": "Y",
        "ASSIGNED_BY_ID": 1,
        "CURRENCY_ID": "USD",
        "OPPORTUNITY": 12500,
        "PHONE": [{"VALUE": "555888", "VALUE_TYPE": "WORK"}]
    },
    'params': {
        "REGISTER_SONET_EVENT": "Y",
    }
}

print(bx24.call('crm.lead.add', data))
