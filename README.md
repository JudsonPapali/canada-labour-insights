
# Canada Labour Insights

Dashboard hospedável que exibe a **taxa de desemprego** (mensal, dessazonalizada) por província/território no Canadá, usando dados oficiais do **Statistics Canada**.

## Live Demo
Após deploy, acesse a raiz do serviço: `/`.

## Endpoints
- `GET /api/regions` → lista de regiões suportadas
- `GET /api/unemployment?geo=Ontario&latest_n=24` → série temporal

## Desenvolvimento
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```
Abra http://localhost:8000

## Deploy com Docker
```bash
docker build -t canada-labour-insights .
docker run -p 8000:8000 canada-labour-insights
```

## Notas de dados
- Fonte: Statistics Canada, tabela 14-10-0287-03 (Full Table CSV, idioma EN). 
- O app baixa e **cacheia** o CSV em `backend/cache/14100287.csv`. Caso o arquivo tenha mais de **7 dias**, é baixado novamente.
- Filtros: `Unemployment rate`, `Both sexes`, `15 years and over`.

## Roadmap
- [+] Comparar múltiplas províncias no mesmo gráfico
- [ ] Exportar PNG/CSV da série exibida
- [ ] Adicionar métricas (média 12m, variação m/m e a/a)
- [ ] Segundo cartão: **CPI** (inflação) e **wages**
- [ ] Internacionalização (EN/PT)

## Licença
MIT
