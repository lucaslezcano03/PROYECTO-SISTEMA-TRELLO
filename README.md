# \# Sistema de Gestión de Tickets Técnicos

# 

# Proyecto desarrollado para la materia de Programación.

# 

# El sistema permite gestionar reclamos técnicos mediante un tablero tipo Trello/Kanban. Está orientado a reclamos de Internet Hogar, permitiendo cargar tickets, asignarlos a técnicos, moverlos entre estados y actualizar los cambios en tiempo real.

# 

# \## Integrantes

# 

# \- Lucas Lezcano

# \- Ximena Caceres

# 

# \## Funcionalidades principales

# 

# \- Inicio de sesión y registro de usuarios.

# \- Roles de usuario: empleado, técnico, supervisor y administrador.

# \- Carga de reclamos técnicos desde formulario web.

# \- Asignación automática de tickets al técnico con menor cantidad de casos asignados.

# \- Reasignación de tickets por parte del supervisor o administrador.

# \- Tablero Kanban con columnas de estado.

# \- Movimiento de tickets mediante drag and drop.

# \- Guardado de posiciones ordenadas dentro de cada columna.

# \- Actualización en tiempo real mediante WebSockets con Django Channels.

# \- Notificaciones por asignación y cambios de estado.

# \- API REST para consultar tickets y verificar el estado del sistema.

# \- Permisos según rol de usuario.

# 

# \## Roles del sistema

# 

# \### Empleado

# 

# \- Puede cargar reclamos.

# \- No puede acceder a la gestión de reclamos.

# 

# \### Técnico

# 

# \- Puede ver los tickets asignados a él.

# \- Puede mover tickets entre columnas.

# \- No puede reasignar tickets.

# 

# \### Supervisor

# 

# \- Puede ver todos los tickets.

# \- Puede mover tickets.

# \- Puede reasignar técnicos.

# \- Puede ver notificaciones.

# 

# \### Administrador

# 

# \- Tiene acceso completo al sistema.

# \- Puede acceder al panel de administración de Django.

# 

# \## Tecnologías utilizadas

# 

# \- Python

# \- Django

# \- Django REST Framework

# \- Django Channels

# \- WebSockets

# \- SQLite

# \- HTML

# \- CSS

# \- JavaScript

# \- Git y GitHub

# 

# \## Instalación y ejecución

# 

# Clonar el repositorio:

# 

# ```bash

# git clone git@github-lucas:lucaslezcano03/PROYECTO-SISTEMA-TRELLO.git

# cd PROYECTO-SISTEMA-TRELLO

