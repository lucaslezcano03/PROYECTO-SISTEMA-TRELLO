from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TicketConsumer(AsyncJsonWebsocketConsumer):
    """
    Mantiene la conexión WebSocket del tablero
    y transmite cambios de tickets.
    """

    async def connect(self):
        usuario = self.scope['user']

        # Solo permite conexiones de usuarios logueados.
        if not usuario.is_authenticated:
            await self.close(code=4401)
            return

        self.nombre_grupo = 'tablero_reclamos'

        # Agrega esta conexión al grupo del tablero.
        await self.channel_layer.group_add(
            self.nombre_grupo,
            self.channel_name
        )

        # Acepta la conexión WebSocket.
        await self.accept()

        # Mensaje de prueba para verificar la conexión.
        await self.send_json({
            'tipo': 'conexion',
            'mensaje': 'WebSocket conectado correctamente.'
        })

    async def disconnect(self, close_code):
        # Elimina la conexión cuando se cierra la página.
        if hasattr(self, 'nombre_grupo'):
            await self.channel_layer.group_discard(
                self.nombre_grupo,
                self.channel_name
            )

    async def ticket_movido(self, event):
        # Envía al navegador el movimiento de un ticket.
        await self.send_json({
            'tipo': 'ticket_movido',
            'ticket_id': event['ticket_id'],
            'columna_id': event['columna_id'],
            'posicion': event['posicion'],
            'nuevo_estado': event['nuevo_estado'],
            'movido_por': event['movido_por'],
        })

    async def ticket_actualizado(self, event):
        # Envía cambios de asignación o edición.
        await self.send_json({
            'tipo': 'ticket_actualizado',
            'ticket_id': event['ticket_id'],
            'columna_id': event['columna_id'],
            'asignado_a_id': event.get('asignado_a_id'),
            'actualizado_por': event['actualizado_por'],
        })