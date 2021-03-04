# LEGO-VISION-COMMAND-USB-Camera-with-EV3-and-ev3dev
Эксперименты с камерой LEGO VISION COMMAND.

Для работы необходимо установить numpy, v4l2, cv2.

sudo apt-get update

sudo apt-get install python3-numpy

sudo apt-get install python3-opencv

Далее, установить v4l2 можно только из pip3, устанавливаем его

sudo apt-get install python3-pip

sudo pip3 install v4l2

С самой библиотекой v4l2 будут проблемы, т.к. она напсиана для python2, а нам нужна под python3. 

Придется внести некоторые изменения, опишу позже.

Для вывода потокового видео в HTTP необходима библиотека flask, устанавливаем

sudo apt-get install python3-flask
