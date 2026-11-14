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
Исходный код приложения: <a href="https://github.com/Ollrins/logger-elk-helm/blob/main/app.py" target="_blank"
   style="display:inline-block;padding:10px 18px;background:#0366d6;color:#fff;
          text-decoration:none;border-radius:6px;font-family:sans-serif;
          font-weight:600;font-size:14px;">
  ➡️ app.py
</a>.

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
 
### Пример с TLS (cert-manager)

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: logger-elk.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: logger-elk-tls
      hosts:
        - logger-elk.example.com
```

### Несколько хостов и путей

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: logger-elk.example.com
      paths:
        - path: /
          pathType: Prefix
        - path: /api
          pathType: Prefix
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
```

## Примеры

### Установка с дефолтными значениями

```bash
helm install logger-elk .
```

### Установка с кастомным образом и репликами

```bash
helm install logger-elk . \
  --set replicaCount=3 \
  --set image.repository=myregistry/logger-elk \
  --set image.tag=v1.0
```

### Установка с Ingress и TLS

```bash
helm install logger-elk . \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=logger-elk.example.com \
  --set ingress.tls[0].secretName=logger-elk-tls \
  --set ingress.tls[0].hosts[0]=logger-elk.example.com
```

### Обновление

```bash
helm upgrade logger-elk . --set replicaCount=2
```

### Удаление

```bash
helm uninstall logger-elk
```

## Проверка на реальном кластере (kind)

```bash
# Установить kind (если нет)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Создать кластер
kind create cluster --name logger-elk-test

# Вариант А: с nginx-образом (для проверки chart'а без своего образа)
helm install logger-elk . \
  --set image.repository=nginx \
  --set image.tag=latest

# Вариант Б: с реальным образом из Docker Hub
# helm install logger-elk . \
#   --set image.repository=ollrins/logger-elk \
#   --set image.tag=1.0

# Проверить
kubectl get pods,svc,deploy

# Удалить
kind delete cluster --name logger-elk-test
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
