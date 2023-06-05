#!/usr/bin/python3

from pyzabbix import ZabbixAPI

# Connexion à l'API Zabbix
zabbix_server = 'https://mobutu.data-expertise.com/'
zabbix_username = ''
zabbix_password = ''

zabbix = ZabbixAPI(zabbix_server)
zabbix.login(zabbix_username, zabbix_password)

# Seuil d'utilisation des ressources
threshold = 0.5

# Nom du groupe d'hôtes à vérifier
group_name = ''

# Fonction pour récupérer les informations sur l'utilisation du CPU et de la RAM
def get_resource_usage(host_id):
    # Récupérer les données d'utilisation du CPU et de la RAM pour un hôte spécifique
    cpu_items = zabbix.item.get(output=['lastvalue'], hostids=[host_id], search={'key_': 'system.cpu.util'})
    ram_items = zabbix.item.get(output=['lastvalue'], hostids=[host_id], search={'key_': 'vm.memory.size[used]'})

    # Récupérer les données max d'utilisation du CPU et de la RAM pour un hôte spécifique
    cpu_max_items = zabbix.item.get(output=['lastvalue'], hostids=[host_id], search={'key_': 'system.cpu.num'})
    ram_max_items = zabbix.item.get(output=['lastvalue'], hostids=[host_id], search={'key_': 'vm.memory.size[total]'})

    if not cpu_items:
        return

    if not ram_items:
        return

    if not cpu_max_items:
        return

    if not ram_max_items:
        return
    
    # Récupérer les valeurs d'utilisation du CPU et de la RAM
    cpu_values = [float(item['lastvalue']) for item in cpu_items]
    ram_values = [float(item['lastvalue']) for item in ram_items]

    #Faire la moyenne des valeurs d'utilisation du CPU et de la RAM
    cpu_average = sum(cpu_values) / len(cpu_values)
    ram_average = sum(ram_values) / len(ram_values)

    #convertir la valeur de la RAM en GB
    ram_average = ram_average / 1024 / 1024 / 1024
    
    # Récupérer les valeurs d'utilisation du CPU et de la RAM
    cpu_percent = float(cpu_average)
    mem_percent = float(ram_average)

    # Récupérer les valeurs max d'utilisation du CPU et de la RAM
    cpu_max = float(cpu_max_items[0]['lastvalue'])

    #convertir la valeur de la RAM max en GB
    ram_max = float(ram_max_items[0]['lastvalue']) / 1024 / 1024 / 1024

    return cpu_percent, mem_percent, cpu_max, ram_max

# Fonction pour recommander des ajustements de ressources
def recommend_resource_adjustment(cpu_percent, mem_size, cpu_max, ram_max):
    if cpu_max != 0:
        #Calculer le rapport entre l'utilisation du CPU et le nombre de CPU
        cpu_ratio = cpu_percent / cpu_max

        #Calculer le rapport entre l'utilisation de la RAM et la RAM totale
        ram_ratio = mem_size / ram_max

        if cpu_ratio < threshold:
            print(f"Informations sur l'hôte : {host['name']}")
            #Calculer le nombre de CPU à supprimer avec un arrondi à l'entier inférieur
            nb_cpu = int(cpu_max - cpu_percent) 
            print(f"Le CPU est sous-utilisé. Vous pouvez réduire le nombre de CPU de {nb_cpu}.")

        if ram_ratio < threshold:
            print(f"Informations sur l'hôte : {host['name']}")
            #Calculer la RAM à supprimer avec un arrondi à l'entier inférieur
            nb_ram = int(ram_max - mem_size)
            print(f"La RAM est sous-utilisée. Vous pouvez réduire la RAM de {nb_ram}.")

# Récupérer le groupe d'hôtes spécifié
group = zabbix.hostgroup.get(output=['groupid'], filter={'name': group_name})
if not group:
    print(f"Le groupe '{group_name}' n'a pas été trouvé.")
    zabbix.logout()
    exit()

group_id = group[0]['groupid']

# Récupérer la liste des hôtes appartenant au groupe
hosts = zabbix.host.get(output=['hostid', 'name'], groupids=[group_id])

# Modifier la boucle principale pour gérer les valeurs None retournées par la fonction get_resource_usage
for host in hosts:
    host_id = host['hostid']
    host_name = host['name']

    # Obtenir les pourcentages d'utilisation du CPU et de la RAM pour l'h


    # Obtenir les pourcentages d'utilisation du CPU et de la RAM pour l'hôte
    resource_usage = get_resource_usage(host_id)
    if resource_usage is None:
        continue

    cpu_percent, mem_percent, cpu_max, ram_max = resource_usage
    recommend_resource_adjustment(cpu_percent, mem_percent, cpu_max, ram_max)

# Déconnexion de l'API Zabbix
zabbix.logout
