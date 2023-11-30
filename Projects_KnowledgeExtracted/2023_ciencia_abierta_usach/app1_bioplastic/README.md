# PROYECTO CIENCIA ABIERTA 2023 - USACH: AI_extract_PDF

## Descripción Breve

Este proyecto desarrolla una herramienta basada en inteligencia artificial para la extracción de conocimiento científico de acceso abierto, enfocada en el desarrollo de bioplásticos de algas marinas. Su objetivo es facilitar la investigación y el análisis de datos en este campo emergente, contribuyendo a la sostenibilidad medioambiental y al avance de la ciencia abierta.

## Tabla de Contenidos

- Introducción
- Estado del Proyecto
- Cómo Empezar
- Uso
- Contribución
- Construido Con
- Autores y Reconocimientos
- Contacto

## Estado del Proyecto

El proyecto se encuentra en una fase activa de desarrollo. Continuamos trabajando en mejorar la funcionalidad, la precisión y la facilidad de uso de la aplicación. Se anima a los usuarios y colaboradores a proporcionar feedback y sugerencias, lo cual es vital para el desarrollo continuo y la mejora del proyecto.

### Futuros desarrollos
- Implementación de algoritmos de acceso abierto.
- Implementación de variables de estado para evitar reejecucciones innecesarias.
- Desarrollar herramientas complementarias para abarcar otros campos de la ciencia sostenible.

## Cómo Empezar

### Prerrequisitos

- Python
- Streamlit
- LangChain
- OpenAI
- PyPDF2
- pdf2image

### Instalación
```
!pip install streamlit==1.28.1
!pip install streamlit-javascript==0.1.5
!pip install streamlit-option-menu==0.3.6
!pip install langchain==0.0.336
!pip install langchain-experimental==0.0.41
!pip install openai==1.3.2
!pip install PyPDF2==3.0.1
!pip install pdf2image==1.16.3
```

## Uso
Abre una terminal en tu entorno usual de python o conda y dirigete a la dirección donde descargaste o clonaste el repositorio. Una vez te encuentres en la carpeta de la aplicación, ejecuta en la terminal: 

```
streamlit run main.py
```

### Flujo de trabajo
1. Página de bienvenida
<image src="resources/workflow/1home.png" alt="Home">
2. Configura tu modelo y llaves de acceso en el panel izquierdo, tambien puedes ajustar algunos parametros del modelo.
<image src="/resources/workflow/2 - config model.png" alt="config model">
3. Se recomienda cerrar el panel lateral al comenzar el flujo de trabajo, de esta forma contarás con mayor espacio para el proceso de extracción. El flujo de trabajo comienza con la sección de INPUT, puedes cargar un archivo PDF para que se comprima y se almacene en la carpeta correspondiente o de lo contrario preparar los documentos con anterioridad en la carpeta mencionada. 
<image src="/resources/workflow/3 - charge file.png" alt="charge file">
4. Luego, debes seleccionar el articulo que deseas procesar.
<image src="/resources/workflow/4 - select pdf.png" alt="select_pdf">
5. En la segunda sección, puedes activar la visualización del PDF para una extracción manual o para verificación de información (si has activado la opción y el PDF no se visualiza, lo más probable es que el tamaño supere el limite máximo de visualización)
<image src="/resources/workflow/5 - see pdf.png" alt="see pdf">
6. Al activar la asistencia, se activa el procesamiento del contenido del PDF. En la primera pestaña, podrás ajustar instrucciones específicas para tu agente, las cuales se guardarán en la carpeta "agents".
<image src="/resources/workflow/6 - config agent.png" alt="confi">
7. En la segunda pestaña podrás seleccionar los agentes que quieres utilizar en caso de extración con instrucciones específica.
<image src="/resources/workflow/7 - select assistance.png" alt="Home">
8. Luego, ya puedes comenzar con tu asistente a solicitar información sobre el documento seleccionado 
<image src="/resources/workflow/8 - response.png" alt="Home">
9. A continuación, se muestra un ejemplo de como puedes ir almacenando el contenido en las etiquetas y como estas se almacenan en un JSON en la carpeta de salida "output"
<image src="/resources/workflow/9 - save item.png" alt="Home">
10. Para cualquier duda, sugerencia o comentario, no dude en contactarnos.
<image src="/resources/workflow/10 - contact.png" alt="Home">


## Contribución

### Cómo Contribuir
Agradecemos cualquier contribución que ayude a mejorar y expandir la herramienta AI_extract_PDF. Si estás interesado en contribuir, por favor sigue estos pasos:
- Familiarízate con el Proyecto: Revisa la documentación y el código fuente para entender mejor el proyecto y sus objetivos.
- Identifica Áreas de Mejora: Puede ser en forma de corrección de errores, desarrollo de nuevas funcionalidades, o mejora de la documentación.
- Discusión de Ideas: Antes de comenzar a trabajar en una contribución significativa, abre un issue para discutir tus ideas con el equipo del proyecto. Esto ayuda a alinear tus propuestas con los objetivos del proyecto y evitar duplicación de esfuerzos.
- Fork y Pull Request: Realiza un fork del repositorio, trabaja en tu contribución en una rama separada y envía un pull request. Asegúrate de seguir las convenciones de codificación y documentación del proyecto.

### Buenas Prácticas
- Escribe código claro y mantenible.
- Incluye comentarios y documentación donde sea necesario.
- Asegúrate de que tus cambios no rompan ninguna funcionalidad existente.
- Añade pruebas para las nuevas funcionalidades.

### Reporte de Errores y Sugerencias
Si encuentras un error o tienes sugerencias para mejorar la herramienta, por favor levanta un issue en el repositorio de GitHub. Proporciona tanta información como sea posible para que podamos entender y abordar el problema eficientemente.

## Autores

- Davor Ibarra Pérez
- María José Galotto López
- Alysia Garmulewicz

## Agradecimientos

- Universidad de Santiago de Chile
- Vicerrectoría de Investigación, Innovación y Creación.
- Equipo INES-USACH (Samanta, Diego, Claudia, Tania y el resto del equipo)
- Agencia Nacional de Investigación y Desarrollo del Gobierno de Chile.

## Contacto

davor.ibarra@usach.cl
