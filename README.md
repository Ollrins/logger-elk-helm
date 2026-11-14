# myapp Helm Chart

Helm chart для Flask-приложения `myapp` с JSON-логами. Демонстрирует production-ready подход к упаковке приложений в Kubernetes: Deployment с probe'ами, Service, Ingress (Nginx) с поддержкой TLS, настраиваемые ресурсы и env через `values.yaml`.

## Что внутри

- **Deployment** — с liveness/readiness probe'ами, resource limits/requests, env из `values.yaml`.
- **Service** — ClusterIP (настраивается через `values.yaml`).
- **Ingress** — Nginx Ingress с поддержкой TLS (cert-manager), аннотаций и нескольких хостов/путей.
- **Helpers** — `_helpers.tpl` для имён и лейблов (стандартная практика Helm).
- **NOTES.txt** — инструкции после `helm install` (port-forward, NodePort, LoadBalancer).
- **values.yaml** — все параметры вынесены, шаблоны не требуют правки.

## Структура

```
myapp-helm/
├── Chart.yaml              # метаданные chart'а (имя, версия, appVersion)
├── values.yaml             # параметры по умолчанию (реплики, образ, порты, ресурсы, ingress)
├── README.md               # документация
├── .gitignore              # игнорирует *.tgz (артефакты сборки)
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

## Установка

```bash
# Клонировать
git clone https://github.com/Ollrins/myapp-helm.git
cd myapp-helm

# Установить с дефолтными значениями
helm install myapp .

## Проверка

```bash
# Линт
helm lint .

# Рендер шаблонов без установки
helm template myapp .

# Рендер с Ingress
helm template myapp . --set ingress.enabled=true

# Упаковка в .tgz
helm package .

## Параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `replicaCount` | Количество реплик | `1` |
| `image.repository` | Репозиторий образа | `elk-myapp` |
| `image.tag` | Тег образа | `latest` |
| `image.pullPolicy` | Политика загрузки образа | `IfNotPresent` |
| `service.type` | Тип Service | `ClusterIP` |
| `service.port` | Порт Service | `8000` |
| `service.targetPort` | Порт контейнера | `8000` |
| `ingress.enabled` | Включить Ingress | `false` |
| `ingress.className` | IngressClass | `nginx` |
| `ingress.annotations` | Аннотации Ingress | `{}` |
| `ingress.hosts` | Список хостов и путей | `myapp.local` |
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
helm install myapp ./myapp-helm \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=myapp.example.com
  
### Пример с TLS (cert-manager)

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com
```

### Несколько хостов и путей

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: myapp.example.com
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
helm install myapp .
```

### Установка с кастомным образом и репликами

```bash
helm install myapp . \
  --set replicaCount=3 \
  --set image.repository=myregistry/myapp \
  --set image.tag=v1.2.3
```

### Установка с Ingress и TLS

```bash
helm install myapp . \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=myapp.example.com \
  --set ingress.tls[0].secretName=myapp-tls \
  --set ingress.tls[0].hosts[0]=myapp.example.com
```

### Обновление

```bash
helm upgrade myapp . --set replicaCount=2
```

### Удаление

```bash
helm uninstall myapp
```

## Проверка на реальном кластере (kind)

```bash
# Установить kind (если нет)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Создать кластер
kind create cluster --name myapp-test

# Установить chart (с nginx-образом, т.к. elk-myapp локально нет)
helm install myapp ./myapp-helm \
  --set image.repository=nginx \
  --set image.tag=latest

# Проверить
kubectl get pods,svc,deploy

# Удалить
kind delete cluster --name myapp-test
```

## Проверка chart'а (без кластера)

```bash
# Линт
helm lint .

# Рендер без Ingress
helm template myapp .

# Рендер с Ingress
helm template myapp . --set ingress.enabled=true

# Проверка, что все документы валидны
helm template myapp . --set ingress.enabled=true | \
  python3 -c "import sys,yaml; [print(d['kind'], '->', d['metadata']['name']) for d in yaml.safe_load_all(sys.stdin) if d]"
```

**Ожидаемый вывод:**
```
Service -> myapp
Deployment -> myapp
Ingress -> myapp
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
