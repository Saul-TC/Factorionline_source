import time
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.traceback import install
from rich.markup import escape
from rich.tree import Tree
from rich import print as rprint
import logging
import random
import sys
import threading

# Instalar el manejador de excepciones de Rich para mostrar trazas bonitas
install(show_locals=True)

# Configurar el logger con RichHandler
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_time=True,
        show_path=True,
        markup=True,
        omit_repeated_times=False,
        tracebacks_extra_lines=2
    )]
)

# Obtener una instancia del logger
logger = logging.getLogger("rich_demo")

# Crear una consola personalizada
console = Console()

def demostrar_logging_basico():
    """Demostración de los niveles básicos de logging"""
    console.rule("[bold blue]Demostración de Niveles de Logging Básicos")
    
    logger.debug("[green]Este es un mensaje de [bold]DEBUG[/bold]")
    logger.info("[cyan]Este es un mensaje de [bold]INFO[/bold]")
    logger.warning("[yellow]Este es un mensaje de [bold]WARNING[/bold]")
    logger.error("[red]Este es un mensaje de [bold]ERROR[/bold]")
    logger.critical("[bold white on red]Este es un mensaje [blink]CRÍTICO[/blink]")
    
    time.sleep(1)

def demostrar_logging_estructurado():
    """Demostración de logging con datos estructurados"""
    console.rule("[bold blue]Logging Estructurado")
    
    # Crear una tabla para mostrar datos estructurados
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Nombre")
    table.add_column("Estado", justify="center")
    table.add_column("Prioridad", justify="right")
    
    table.add_row("1", "Proceso A", "[green]Activo[/green]", "Alto")
    table.add_row("2", "Proceso B", "[yellow]Pendiente[/yellow]", "Medio")
    table.add_row("3", "Proceso C", "[red]Inactivo[/red]", "Bajo")
    
    logger.info("Datos de procesos:\n%s", table)
    
    # Crear un árbol jerárquico
    tree = Tree("[bold]Estructura del Proyecto[/bold]")
    src_branch = tree.add("📁 [bold blue]src[/bold blue]")
    src_branch.add("📄 [green]main.py[/green]")
    
    modules_branch = src_branch.add("📁 [bold blue]modules[/bold blue]")
    modules_branch.add("📄 [green]utils.py[/green]")
    modules_branch.add("📄 [green]models.py[/green]")
    
    tests_branch = tree.add("📁 [bold blue]tests[/bold blue]")
    tests_branch.add("📄 [green]test_unit.py[/green]")
    tests_branch.add("📄 [green]test_integration.py[/green]")
    
    logger.info("Visualizando estructura del proyecto:\n%s", tree)
    
    time.sleep(1)

def simular_tarea(nombre, duracion):
    """Simula una tarea con progreso"""
    for i in range(duracion):
        # Dormimos un tiempo aleatorio para simular trabajo
        time.sleep(random.uniform(0.01, 0.2))
        # Registramos cada paso de progreso
        if i == duracion // 2:
            logger.info(f"Tarea '{nombre}' al 50%%")
        
        # Simular un error aleatorio
        if random.random() < 0.01:
            try:
                raise ValueError(f"Error simulado en la tarea '{nombre}'")
            except ValueError as e:
                logger.error("Error en la tarea: %s", e)

def demostrar_logging_excepciones():
    """Demostración de logging de excepciones con trazas mejoradas"""
    console.rule("[bold blue]Logging de Excepciones")
    
    try:
        # Simular un error con varios niveles de llamada
        def funcion_c(valor):
            return 100 / valor
        
        def funcion_b():
            return funcion_c(0)
        
        def funcion_a():
            datos = {"nombre": "Prueba", "valor": None}
            resultado = funcion_b()
            return datos["valor"] + resultado
        
        logger.info("Intentando operación que causará excepción...")
        funcion_a()
    except Exception as e:
        logger.exception("Se ha producido un error durante la ejecución")
    
    time.sleep(1)

def demostrar_logging_concurrente():
    """Demostración de logging desde múltiples hilos"""
    console.rule("[bold blue]Logging Concurrente")
    
    def tarea_en_hilo(id_hilo):
        logger.info(f"[bold]Hilo {id_hilo}[/bold] iniciado")
        for i in range(3):
            logger.debug(f"Hilo {id_hilo}: Paso {i+1}")
            time.sleep(random.uniform(0.1, 0.5))
        logger.info(f"[bold]Hilo {id_hilo}[/bold] finalizado")
    
    # Crear y ejecutar varios hilos
    hilos = []
    for i in range(1, 4):
        hilo = threading.Thread(target=tarea_en_hilo, args=(i,))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que todos los hilos terminen
    for hilo in hilos:
        hilo.join()
    
    time.sleep(1)

def demostrar_logging_con_progreso():
    """Demostración de logging con barras de progreso integradas"""
    console.rule("[bold blue]Logging con Barras de Progreso")
    
    logger.info("Iniciando tareas con seguimiento de progreso")
    
    # Usar el administrador de contexto de Progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        # Crear varias tareas
        tarea1 = progress.add_task("[green]Procesando datos...", total=100)
        tarea2 = progress.add_task("[cyan]Analizando resultados...", total=100)
        tarea3 = progress.add_task("[yellow]Generando informe...", total=100)
        
        # Simular progreso
        while not progress.finished:
            # Actualizar progreso
            progress.update(tarea1, advance=random.uniform(0.5, 2.0))
            progress.update(tarea2, advance=random.uniform(0.2, 1.0))
            progress.update(tarea3, advance=random.uniform(0.1, 0.5))
            
            # Añadir logs ocasionales que se muestran entre las barras de progreso
            if random.random() < 0.1:
                nivel = random.choice(["debug", "info", "warning"])
                if nivel == "debug":
                    logger.debug("Procesando bloque de datos...")
                elif nivel == "info":
                    logger.info("Resultados intermedios calculados")
                else:
                    logger.warning("Detectada posible anomalía en los datos")
            
            time.sleep(0.1)
    
    logger.info("[bold green]¡Todas las tareas completadas![/bold green]")
    time.sleep(1)

def demostrar_contextos_logging():
    """Demostración de logging con contextos para agrupar mensajes relacionados"""
    console.rule("[bold blue]Logging con Contextos")
    
    # Simular un flujo de trabajo con contextos
    logger.info("[bold]Iniciando flujo de procesamiento de datos[/bold]")
    
    # Contexto 1: Carga de datos
    panel = Panel("[bold]Contexto: Carga de Datos[/bold]", 
                 border_style="blue", 
                 expand=False)
    logger.info(f"\n{panel}")
    
    logger.debug("Conectando a la base de datos...")
    time.sleep(0.5)
    logger.info("[green]Conexión exitosa a la base de datos[/green]")
    time.sleep(0.3)
    logger.debug("Ejecutando consulta SQL...")
    time.sleep(0.7)
    logger.info("[green]Datos recuperados correctamente[/green]")
    
    # Contexto 2: Procesamiento
    panel = Panel("[bold]Contexto: Procesamiento[/bold]", 
                 border_style="cyan", 
                 expand=False)
    logger.info(f"\n{panel}")
    
    logger.debug("Iniciando transformación de datos...")
    time.sleep(0.6)
    logger.warning("[yellow]Algunos registros contienen valores nulos[/yellow]")
    time.sleep(0.4)
    logger.info("Aplicando reglas de limpieza...")
    time.sleep(0.5)
    logger.info("[green]Procesamiento completado[/green]")
    
    # Contexto 3: Resultados
    panel = Panel("[bold]Contexto: Resultados[/bold]", 
                 border_style="green", 
                 expand=False)
    logger.info(f"\n{panel}")
    
    logger.debug("Calculando estadísticas...")
    time.sleep(0.5)
    
    # Crear una tabla para mostrar resultados
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Métrica")
    table.add_column("Valor", justify="right")
    
    table.add_row("Total registros", "1,250")
    table.add_row("Registros válidos", "1,180")
    table.add_row("Tiempo de proceso", "2.3s")
    table.add_row("Uso de memoria", "45MB")
    
    logger.info("Resumen de resultados:\n%s", table)
    logger.info("[bold green]Flujo completado exitosamente[/bold green]")
    
    time.sleep(1)

def ejecutar_demo_completa():
    """Ejecuta una demostración completa de las capacidades de Rich logging"""
    console.clear()
    
    # Título principal
    titulo = Panel(
        "[bold blue]DEMOSTRACIÓN DEL SISTEMA DE LOGGING DE RICH[/bold blue]",
        border_style="blue",
        expand=False
    )
    console.print(titulo)
    console.print()
    
    # Mostrar información del sistema
    logger.info(f"[bold]Sistema[/bold]: {sys.platform}")
    logger.info(f"[bold]Python[/bold]: {sys.version.split()[0]}")
    logger.info(f"[bold]Terminal[/bold]: {console.width}x{console.height}")
    logger.info(f"[bold]Modo Color[/bold]: {'Activado' if console.color_system else 'Desactivado'}")
    
    # Ejecutar todas las demostraciones
    time.sleep(1)
    demostrar_logging_basico()
    demostrar_logging_estructurado()
    demostrar_logging_excepciones()
    demostrar_logging_concurrente()
    demostrar_logging_con_progreso()
    demostrar_contextos_logging()
    
    # Mensaje final
    console.rule("[bold green]Demostración Completada")
    logger.info("[bold green]La demostración del sistema de logging de Rich ha finalizado[/bold green]")
    logger.info("Esta demostración ha cubierto las siguientes características:")
    
    # Lista de características demostradas
    caracteristicas = [
        "Niveles de logging con formato y colores",
        "Trazas de excepción mejoradas",
        "Datos estructurados (tablas y árboles)",
        "Logging concurrente desde múltiples hilos",
        "Integración con barras de progreso",
        "Contextos de logging",
        "Paneles y estilos personalizados"
    ]
    
    for i, caracteristica in enumerate(caracteristicas, 1):
        logger.info(f"[cyan]{i}.[/cyan] {caracteristica}")
    
    console.print()
    console.print("[bold]¡Gracias por ver la demostración![/bold]")

if __name__ == "__main__":
    ejecutar_demo_completa()