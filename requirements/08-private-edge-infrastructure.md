# Private, Edge And Infrastructure

CloudRING должен быть облачной платформой, которая работает не только в public
cloud.
Private cloud, edge, single-host и disconnected deployment - полноценные
продуктовые сценарии.

## OpenSource Инсталляция

| ID | Требование | Почему |
|---|---|---|
| CR-INFRA-001 | Пользователь должен иметь возможность скачать и развернуть базовую CloudRING-инсталляцию на своем сервере или группе серверов. | Это ключевой способ снизить lock-in и войти в платформу. |
| CR-INFRA-002 | Базовая инсталляция должна включать минимальные cloud capability: identity, resource manager, compute, network, storage, monitoring, update channel. | Без этих capability инсталляция не является облачной платформой. |
| CR-INFRA-003 | Single-host deployment должен быть поддержан как learning/dev/small сценарий. | Не каждый пользователь начинает с кластера. |
| CR-INFRA-004 | Multi-node deployment должен поддерживать production/private сценарии. | Private cloud требует отказоустойчивости и масштабирования. |
| CR-INFRA-005 | Инсталляция должна иметь clear upgrade path от single-host к multi-node. | Малый старт не должен становиться тупиком. |
| CR-INFRA-006 | Базовая инсталляция должна уметь подключаться к federation или работать автономно. | Пользователь может выбирать уровень зависимости от внешней сети. |

## Private Cloud

| ID | Требование | Почему |
|---|---|---|
| CR-INFRA-007 | Private cloud сценарий должен поддерживать enterprise extensions без потери совместимости с Open Cloud Standard. | Enterprise нуждается в процессах и интеграциях, но не должен выпадать из экосистемы. |
| CR-INFRA-008 | Private cloud должен поддерживать интеграцию с корпоративными identity, network, audit, billing/showback и approval processes. | Внутренняя инфраструктура живет в бизнес-процессах организации. |
| CR-INFRA-009 | Private cloud должен иметь возможность использовать selected public/federated services, если они нецелесообразны внутри private-инфраструктуры. | Не все сервисы стоит разворачивать локально. |
| CR-INFRA-010 | Private cloud должен поддерживать policy запрета внешнего использования сервисов. | Некоторые клиенты не могут выводить workload или данные наружу. |
| CR-INFRA-011 | Private cloud должен сохранять работоспособность при окончании maintenance subscription. | Клиент сохраняет контроль над своей инфраструктурой. |

## Edge

| ID | Требование | Почему |
|---|---|---|
| CR-INFRA-012 | Edge deployment должен поддерживать ограниченный набор сервисов, выбранный под latency, geography и автономность. | Edge не является маленькой копией полного public cloud. |
| CR-INFRA-013 | Edge должен поддерживать connected mode с синхронизацией в federation. | Для управления, billing и updates нужна связь с остальной сетью. |
| CR-INFRA-014 | Edge должен поддерживать disconnected mode с локальным control plane минимум для критичных функций. | Связь на edge может быть нестабильной или запрещенной. |
| CR-INFRA-015 | Edge должен иметь модель delayed sync для usage, audit и catalog events. | События не должны теряться при временном отсутствии связи. |
| CR-INFRA-016 | Edge должен иметь ограниченные resource profiles и policy для размещения workload. | Edge-ресурсы меньше и дороже, чем центральные площадки. |

## Infrastructure Supply

| ID | Требование | Почему |
|---|---|---|
| CR-INFRA-017 | CloudRING должен поддерживать bare metal management как capability. | Private и edge часто начинаются с физических серверов. |
| CR-INFRA-018 | Платформа должна поддерживать VM template/image factory для базовых ОС и service images. | Воспроизводимые образы ускоряют deployment и уменьшают drift. |
| CR-INFRA-019 | VM/host-шаблоны должны поддерживать стандартный механизм первичной настройки гостевой системы с profile-scoped resolver/mirror/network policy, private/offline mode и отсутствием скрытой endpoint dependency. | Автоматическое provisioning невозможно без bootstrap, но bootstrap не должен прятать инфраструктурную зависимость. |
| CR-INFRA-020 | VM/host-шаблоны должны поддерживать автоматическое расширение диска/разделов или эквивалентный lifecycle storage resize with first-boot validation and degraded/blocked state when resize support is absent. | Размеры дисков и окружения различаются, а молчаливый failure ломает self-service. |
| CR-INFRA-021 | VM-шаблоны должны поддерживать serial console/debug access для аварийных ситуаций with profile state, approval, scope, retention, redaction and audit. | История эксплуатации показывает, что без консоли восстановление сложнее, но diagnostic access сам является trust boundary. |
| CR-INFRA-022 | VM-шаблоны должны поддерживать crash dump для диагностики kernel/system failures with enabled/disabled profile state, collection boundary, retention and redaction. | Глубокие инциденты требуют посмертной диагностики без утечки sensitive operational data. |
| CR-INFRA-023 | VM/host-шаблоны должны включать интеграцию с целевой средой виртуализации или hardware management как capability features: shutdown, network, time/signal visibility, support diagnostics and graceful degradation. | Без такой интеграции страдает эксплуатация, но контракт должен быть replaceable и не привязан к одному backend. |
| CR-INFRA-024 | Образы должны очищаться от временных файлов, истории, build-следов и небезопасных доступов перед публикацией, сохраняя redacted pre/post cleanup manifest outside the image. | Базовый образ не должен утекать операционной памятью сборки, а cleanup должен быть доказуемым и повторяемым. |
| CR-INFRA-025 | Сборка образов должна поддерживать encrypted variables/secrets, machine-readable field classes and source-safety review for current and history/deleted-path material. | История источников показывает риск секретов в инфраструктурных repo and generated build evidence. |

## Cross-Cloud Connect

| ID | Требование | Почему |
|---|---|---|
| CR-INFRA-026 | CloudRING должен поддерживать cross-cloud connectivity между public, private и edge presence. | Федерация без сети не дает переносимости. |
| CR-INFRA-027 | Cross-cloud connect должен учитывать latency, encryption, routing policy и jurisdiction. | Не всякая связь допустима и полезна. |
| CR-INFRA-028 | Платформа должна показывать пользователю, какие cross-provider маршруты используются сервисом. | Прозрачность нужна для доверия и compliance. |
| CR-INFRA-029 | DR/backup/replication через cross-cloud connect должны быть policy-aware. | Резервная копия в запрещенной зоне нарушает требования пользователя. |
