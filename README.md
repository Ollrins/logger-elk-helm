# Logger-elk Helm Chart

Helm chart для Flask-приложения `logger-elk` с JSON-логами. Демонстрирует production-ready подход к упаковке приложений в Kubernetes: Deployment с probe'ами, Service, Ingress (Nginx) с поддержкой TLS, настраиваемые ресурсы и env через `values.yaml`.

## Что внутри

- **Deployment** — с liveness/readiness probe'ами, resource limits/requests, env из `values.yaml`.
- **Service** — ClusterIP (настраивается через `values.yaml`).
- **Ingress** — Nginx Ingress с поддержкой TLS (cert-manager), аннотаций и нескольких хостов/путей.
- **Helpers** — `_helpers.tpl` для имён и лейблов (стандартная практика Helm).
- **NOTES.txt** — инструкции после `helm install` (port-forward, NodePort, LoadBalancer).
- **values.yaml** — все параметры вынесены, шаблоны не требуют правки.

## Структура

```
logger-elk-helm/
├── Chart.yaml              # метаданные chart'а (имя, версия, appVersion)
├── values.yaml             # параметры по умолчанию (реплики, образ, порты, ресурсы, ingress)
├── app.py                  # исходный код Flask-приложения (JSON-логи)
└── templates/
    ├── _helpers.tpl        # хелперы для имён и лейблов
    ├── deployment.yaml     # Deployment с probe'ами, resources, env
    ├── service.yaml        # Service (ClusterIP)
    ├── ingress.yaml        # Ingress (Nginx) с TLS и аннотациями
    └── NOTES.txt           # инструкции после helm install
```

## Требования

- Kubernetes >= 1.19 (для `networking.k8s.io/v1` Ingress)
- Helm >= 3.0
- (Опционально) Nginx Ingress Controller — если включаете `ingress.enabled`
- (Опционально) cert-manager — если используете TLS

## Образ

Chart использует образ `ollrins/logger-elk:1.0` из Docker Hub.
Исходный код приложения: **➡️ [`app.py`](https://github.com/Ollrins/logger-elk-helm/blob/main/app.py)**.

## Установка

```bash
# Клонировать
git clone https://github.com/Ollrins/logger-elk-helm.git
cd logger-elk-helm

# Установить с дефолтными значениями
helm install logger-elk .
```

## Параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `replicaCount` | Количество реплик | `1` |
| `image.repository` | Репозиторий образа | `ollrins/logger-elk` |
| `image.tag` | Тег образа | `1.0` |
| `image.pullPolicy` | Политика загрузки образа | `IfNotPresent` |
| `service.type` | Тип Service | `ClusterIP` |
| `service.port` | Порт Service | `8000` |
| `service.targetPort` | Порт контейнера | `8000` |
| `ingress.enabled` | Включить Ingress | `false` |
| `ingress.className` | IngressClass | `nginx` |
| `ingress.annotations` | Аннотации Ingress | `{}` |
| `ingress.hosts` | Список хостов и путей  (объекты `host` + `paths`) | `[{host: logger-elk.local, paths: [{path: /, pathType: Prefix}]}]` |
| `ingress.tls` | TLS-секреты | `[]` |
| `resources.limits.cpu` | CPU лимит | `200m` |
| `resources.limits.memory` | Memory лимит | `256Mi` |
| `resources.requests.cpu` | CPU запрос | `100m` |
| `resources.requests.memory` | Memory запрос | `128Mi` |
| `env.LOG_LEVEL` | Уровень логирования | `INFO` |
| `nodeSelector` | Node selector | `{}` |
| `tolerations` | Tolerations | `[]` |
| `affinity` | Affinity | `{}` |


## Ingress

Chart поддерживает Nginx Ingress. По умолчанию выключен.

### Включить Ingress

```bash
helm install logger-elk . \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=logger-elk.example.com
 ``` 

## Примеры

### Установка с дефолтными значениями

```bash
helm install logger-elk .
```

### Обновление

```bash
helm upgrade logger-elk . --set replicaCount=2
```

### Удаление

```bash
helm uninstall logger-elk
```

## Проверка chart'а (без кластера)

```bash
# Линт
helm lint .

# Рендер без Ingress
helm template logger-elk .

# Рендер с Ingress
helm template logger-elk . --set ingress.enabled=true

# Проверка, что все документы валидны
helm template logger-elk . --set ingress.enabled=true | \
  python3 -c "import sys,yaml; [print(d['kind'], '->', d['metadata']['name']) for d in yaml.safe_load_all(sys.stdin) if d]"
```

**Ожидаемый вывод:**
```
Service -> logger-elk
Deployment -> logger-elk
Ingress -> logger-elk
```

## Стек

| Компонент | Версия | Роль |
|-----------|--------|------|
| Helm | >= 3.0 | Пакетный менеджер Kubernetes |
| Kubernetes | >= 1.19 | Платформа оркестрации |
| Nginx Ingress Controller | — | Ingress (опционально) |
| cert-manager | — | TLS-сертификаты (опционально) |

## Лицензия

MIT
