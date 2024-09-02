# Usamos la imagen oficial de Redis como base
FROM redis:latest

# Establecemos un volumen para los datos persistentes de Redis
VOLUME ["/data"]

# Exponemos el puerto predeterminado de Redis
EXPOSE 6379

# Comando por defecto para ejecutar Redis
CMD ["redis-server"]
