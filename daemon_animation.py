# Libreries
import asyncio
import random
import time
# Dependencies
from dependencies.animation import Animator
from dependencies.queue import QueueExpression


async def main():
    # Iniciando VTubeStudio
    animator = Animator(ip="172.28.32.1", port="8001")
    # Iniciando animación base
    await animator.animate(f"base_{random.randint(1, 5)}")
    animation_duration = random.randint(15, 25)
    animation_timer = time.time()
    # Conectando con redis
    expression_queue = QueueExpression('expressions')
    expression_timer = time.time()
    expression_status = False
    expression = None

    while True:
        # Caso: Actualizando animación base
        if time.time() - animation_timer > animation_duration:
            await animator.animate(f"base_{random.randint(1, 5)}")
            animation_duration = random.randint(15, 25)
            animation_timer = time.time()
        
        # Obteniendo expresiones
        expressions = expression_queue.dequeue()

        # Caso: Existen una expresión activa
        if expression_status and time.time() - expression_timer > 8:
            await animator.animate(f'expression_{expression}')
            expression_status = False

        # Caso: Existen expresiones en la memoria
        if len(expressions) > 0:
            expression = expressions[-1]
            await animator.animate(f'expression_{expression}')
            expression_timer = time.time()
            expression_status = True

        time.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
