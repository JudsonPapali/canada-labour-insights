# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Define variável de ambiente do Render
ENV PORT=8000

# Expõe a porta do Render
EXPOSE 8000

# Comando de inicialização
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"]

