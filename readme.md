# Подготовка сервера 

## Создание контейнера

Создайте файл с именем <span style="color:red;">docker-compose.yaml</span>

Со следующим содержанием:

```
version: '3.5'

services:
  db_auth:
    container_name: db_auth
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=root
      - POSTGRES_USER=admin
    image: postgres:14.3-alpine
```

## Установка git

```
sudo apt-get update
sudo apt-get install git
```

## Установка docker 
```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Установка docker-compose

```
apt indyall docker-compose
```

## Запуск 

```
docker-compose up --build
``` 

## Остановка контейнера

```
docker-compose down
```

Эта команда остановит и удалит все контейнеры. Она также удалит сети, которые были созданы для ваших контейнеров, и освободит ресурсы, занятые контейнерами.

Если вы хотите остановить контейнеры без их удаления, вы можете использовать команду

```
docker-compose stop
```
Эти контейнеры остановятся, но останутся в системе. Запустить их заново можно командой

```
docker-compose start
```