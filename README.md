# LEGO-VISION-COMMAND-USB-Camera-with-EV3-and-ev3dev
Эксперименты с камерой LEGO VISION COMMAND.

Добавить архивный репозиторий, т.к. Дебиан с 2022 года, перевела подедржку 9 го релиза в архив

sudo nano /etc/apt/sources.list

Вместо

deb http://httpredir.debian.org/debian stretch main contrib non-free

Добавляем строку

deb http://archive.debian.org/debian stretch main contrib non-free

Вместо

deb http://security.debian.org/ stretch/updates main contrib non-free

Добавляем строку

deb http://archive.debian.org/debian-security/ stretch/updates main contrib non-free


Для работы необходимо установить numpy, v4l2, cv2 и flask.

sudo apt-get update

sudo apt-get upgrade

sudo apt-get install python3-numpy

sudo apt-get install python3-opencv

Далее, установить v4l2 можно только из pip3, устанавливаем его

sudo apt-get install python3-pip

sudo pip3 install v4l2

С самой библиотекой v4l2 будут проблемы, т.к. она написана для python2, а нам нужна под python3. 

Решение проблемы с ошибкой импорта v412 описано в файле "решение проблемы с v412.txt"

Для вывода потокового видео в HTTP необходима библиотека flask, устанавливаем

sudo apt-get install python3-flask
