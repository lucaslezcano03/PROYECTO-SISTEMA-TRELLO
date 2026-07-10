# Sistema de Gestión de Tickets Técnicos

Proyecto desarrollado para la materia **Programación**.

El sistema permite gestionar reclamos técnicos mediante un tablero tipo **Trello/Kanban**, orientado a reclamos de **Internet Hogar**.  
Permite cargar tickets, asignarlos a técnicos, moverlos entre estados, mantener posiciones ordenadas y actualizar cambios en tiempo real mediante WebSockets.

---

## Integrantes

- Lucas Lezcano
- Ximena Caceres

---

## Objetivo del proyecto

El objetivo principal del sistema es organizar y administrar reclamos técnicos de forma clara, permitiendo que los usuarios trabajen según su rol dentro del sistema.

El proyecto está inspirado en el funcionamiento de herramientas tipo Trello, adaptado a un contexto de soporte técnico.

---

## Funcionalidades principales

- Inicio de sesión y registro de usuarios.
- Roles de usuario: empleado, técnico, supervisor y administrador.
- Carga de reclamos técnicos desde formulario web.
- Asignación automática de tickets al técnico con menor cantidad de casos asignados.
- Reasignación de tickets por parte del supervisor o administrador.
- Tablero Kanban con columnas de estado.
- Movimiento de tickets mediante drag and drop.
- Guardado de posiciones ordenadas dentro de cada columna.
- Actualización en tiempo real mediante WebSockets con Django Channels.
- Notificaciones por asignación y cambios de estado.
- API REST para consultar tickets y verificar el estado del sistema.
- Permisos según el rol del usuario.

---

## Roles del sistema

### Empleado

- Puede cargar reclamos.
- No puede acceder a la gestión general de reclamos.
- No puede mover tickets ni reasignar técnicos.

### Técnico

- Puede ver los tickets asignados a él.
- Puede mover sus tickets entre columnas.
- Puede ver sus notificaciones.
- No puede reasignar tickets.

### Supervisor

- Puede ver todos los tickets.
- Puede mover tickets entre columnas.
- Puede reasignar técnicos.
- Puede ver notificaciones.

### Administrador

- Tiene acceso completo al sistema.
- Puede acceder al panel de administración de Django.
- Puede administrar usuarios, tickets, tableros y demás datos del sistema.

---

## Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- Django Channels
- WebSockets
- SQLite
- HTML
- CSS
- JavaScript
- Git
- GitHub

---

## Estructura principal del proyecto

```text
PROYECTO-SISTEMA-TRELLO/
│
├── apps/
│   ├── users/
│   ├── boards/
│   ├── tickets/
│   └── notifications/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
│
├── templates/
│   ├── tickets/
│   ├── notifications/
│   └── registration/
│
├── static/
│   └── css/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Instalación y ejecución

Clonar el repositorio:

```cmd
git clone git@github.com:lucaslezcano03/PROYECTO-SISTEMA-TRELLO.git
cd PROYECTO-SISTEMA-TRELLO
```

Crear entorno virtual:

```cmd
python -m venv venv
```

Activar entorno virtual en Windows:

```cmd
venv\Scripts\activate
```

Instalar dependencias:

```cmd
pip install -r requirements.txt
```

Aplicar migraciones:

```cmd
python manage.py migrate
```

Crear superusuario:

```cmd
python manage.py createsuperuser
```

Ejecutar el servidor:

```cmd
python manage.py runserver
```

Abrir en el navegador:

```text
http://127.0.0.1:8000/
```

---

## Rutas principales

```text
/accounts/login/              Inicio de sesión
/accounts/register/           Registro de usuarios
/tickets/nuevo-reclamo/       Carga de reclamos
/tickets/gestion/             Tablero de gestión
/notificaciones/              Notificaciones
/admin/                       Panel administrativo
```

---

## API REST

La API fue implementada con **Django REST Framework** y requiere autenticación.

### Estado del sistema

```text
GET /api/estado/
```

Devuelve información general del sistema, usuario autenticado y rol.

Ejemplo de respuesta:

```json
{
    "ok": true,
    "sistema": "Sistema de Tickets Técnicos",
    "api": "activa",
    "usuario": "lucas",
    "rol": "admin",
    "mensaje": "Backend funcionando correctamente."
}
```

### Listado de tickets

```text
GET /api/tickets/
```

Devuelve los tickets disponibles según el rol del usuario.

Ejemplo de respuesta:

```json
{
    "ok": true,
    "cantidad": 3,
    "tickets": []
}
```

### Crear ticket desde API

```text
POST /api/tickets/
```

Ejemplo de JSON:

```json
{
    "numero_contrato": "99887766",
    "id_cliente": "11223344",
    "correo_cliente": "cliente.demo@gmail.com",
    "contacto_principal": "0981123456",
    "contacto_secundario": "0971123456",
    "tipo_interaccion": "reclamo",
    "comentario": "Prueba de carga de reclamo desde la API."
}
```

---

## WebSockets

El sistema utiliza **Django Channels** para actualizar el tablero en tiempo real.

Ruta WebSocket:

```text
ws://127.0.0.1:8000/ws/tickets/
```

Cuando un ticket se mueve en el tablero, se envía un evento como:

```json
{
    "tipo": "ticket_movido",
    "ticket_id": 3,
    "columna_id": 2,
    "posicion": 0,
    "nuevo_estado": "En seguimiento",
    "movido_por": "lucas"
}
```

Esto permite que otros usuarios conectados vean el movimiento del ticket sin actualizar manualmente la página.

---

## Pruebas realizadas

- Inicio de sesión por roles.
- Carga de reclamos.
- Asignación automática a técnicos.
- Reasignación de tickets.
- Movimiento de tickets mediante drag and drop.
- Guardado de posición de tickets.
- Actualización en tiempo real con WebSockets.
- Notificaciones.
- API desde navegador, consola y terminal.
- Validación de permisos por rol.

---

## Estado del proyecto

El sistema se encuentra funcional para la gestión de reclamos técnicos.

Cumple con las funcionalidades principales solicitadas:

- usuarios;
- tableros;
- listas o columnas;
- tarjetas o tickets;
- permisos por usuario;
- drag and drop con posiciones ordenadas;
- WebSockets con Django Channels;
- asignación de tickets;
- notificaciones;
- API REST.

---

## Repositorio

Proyecto desarrollado y versionado con Git y GitHub mediante ramas de trabajo por integrante.
