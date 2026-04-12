Nombre del módulo: Daily Tasks
Objetivo del módulo
Desarrollar un módulo sencillo de tareas diarias que permita al administrador configurar actividades repetitivas que deben aparecer todos los días para los usuarios. El usuario normal podrá visualizar sus tareas diarias y marcarlas como completadas según las vaya realizando.
El objetivo es dar continuidad a hábitos y actividades repetitivas, guardando en base de datos el cumplimiento diario para futuras consultas o reportes.

Alcance funcional
El módulo debe mostrar todos los días las mismas tareas configuradas, permitiendo que el usuario:
•	complete una tarea, 
•	complete varias, 
•	o no complete ninguna. 
Cada día debe registrarse de forma independiente, para conservar el historial de cumplimiento diario.

Roles
Administrador
Podrá:
•	Crear tareas diarias 
•	Editar tareas existentes 
•	Activar o desactivar tareas 
•	Definir el orden de visualización 
Usuario normal
Podrá:
•	Ver el listado de tareas del día 
•	Marcar una tarea como completada 
•	Desmarcarla si fue marcada por error 
•	Consultar únicamente las tareas visibles/activas 

Comportamiento esperado del módulo
•	Las tareas configuradas deben aparecer automáticamente todos los días. 
•	Las tareas son recurrentes diarias. 
•	El cumplimiento debe guardarse por fecha. 
•	Marcar una tarea como completada en un día no debe afectar el estado de esa misma tarea en otro día. 
•	El sistema debe permitir que un día el usuario complete todas, algunas o ninguna. 
•	La información debe quedar almacenada en base de datos para futuros reportes, aunque en esta fase no se desarrollen reportes. 

Tareas iniciales que deben salir todos los días
Estas son las tareas base que se mostrarán diariamente:
•	Speaking alone 
•	Shadowing 
•	Phrase memorization 
•	Assisted writing 
•	Copywork 
•	Handwriting 
•	Anki 
•	Blinkist 
•	Busuu 
•	Cake 
•	TV Shows 
•	Word Trails 

Estructura simple del módulo
1. Administrador de tareas
Pantalla para mantenimiento de tareas, con los campos:
•	Nombre de la tarea 
•	Descripción corta opcional 
•	Estado: activa / inactiva 
•	Orden de visualización 
Acciones:
•	Crear 
•	Editar 
•	Guardar 
•	Activar / desactivar 

2. Pantalla de tareas diarias para usuario
Pantalla donde el usuario visualiza las tareas correspondientes al día actual.
Debe mostrar:
•	Fecha actual 
•	Listado de tareas activas 
•	Checkbox o botón de completar por cada tarea 
•	Estado de cumplimiento del día 
Ejemplo:
Fecha: 10/04/2026
•	Speaking alone 
•	Shadowing 
•	Phrase memorization 
•	Anki 

Reglas funcionales
1.	Las tareas activas deben mostrarse todos los días automáticamente. 
2.	Cada tarea debe poder marcarse como completada una sola vez por día. 
3.	Si el usuario desmarca la tarea, el sistema debe actualizar el estado del día. 
4.	El historial debe guardarse por: 
o	usuario 
o	tarea 
o	fecha 
o	estado de cumplimiento 
5.	Si una tarea está inactiva, no debe mostrarse al usuario. 
6.	El administrador puede editar el nombre o configuración de la tarea sin afectar el historial ya guardado. 
7.	No se requiere lógica compleja de metas, puntajes ni recordatorios en esta fase. 

Estructura de datos sugerida
Tabla: tareas
•	id_tarea 
•	nombre 
•	descripcion 
•	estado 
•	orden 
•	fecha_creacion 
•	fecha_modificacion 
Tabla: tarea_diaria_usuario
•	id_registro 
•	id_tarea 
•	id_usuario 
•	fecha 
•	completada 
•	fecha_hora_registro 
Con esto ya podrás guardar el cumplimiento diario y luego usarlo para reportes.

Requerimiento funcional formal
Se requiere desarrollar un módulo de tareas diarias que permita configurar actividades repetitivas para ser mostradas automáticamente todos los días a los usuarios.
El módulo contará con un administrador de tareas, donde un usuario con perfil administrador podrá crear, editar, activar o desactivar tareas diarias.
Los usuarios normales podrán visualizar las tareas activas del día y marcar cada una como completada. El cumplimiento deberá registrarse por fecha y por usuario, de manera que el sistema conserve el historial diario de tareas realizadas.
El módulo deberá ser sencillo, enfocado únicamente en la visualización diaria de tareas repetitivas y el registro de cumplimiento, dejando preparada la información en base de datos para futuros reportes.

Recomendación Para no complicarlo, arranca con esto:
•	catálogo de tareas 
•	activas / inactivas 
•	listado diario 
•	checkbox de completar 
•	guardado por fecha y usuario 

