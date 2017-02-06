# Анализ Источников

Этот документ фиксирует, какие источники легли в требования.
Он не является пересказом исходников и не должен использоваться для переноса
кода, конфигураций или внутренних операционных деталей.

## Область Анализа

Разобраны источники:

- `CloudRING_en.pdf` - презентация идеи CloudRING.
- `legacy source bundle` - локальная папка пользователя с прототипами,
  документацией, историей git и эксплуатационными материалами.

Для legacy source bundle выполнена инвентаризация файлов без прямого включения
`vendor`, `node_modules` и `.git`.
Найдено 418 значимых файлов в рабочих деревьях.
Подробный coverage manifest and completion audit находится в
[26-source-coverage-and-completion-audit.md](26-source-coverage-and-completion-audit.md).
`SRC-PASS-007` добавляет classification closure: все 418 значимых файлов
отнесены к обезличенным source classes после common-noise exclusions, но это не
является full line-by-line или full-history audit.

| Область | Файлов | Роль В Анализе |
|---|---:|---|
| Legacy platform prototype | 241 | Основной прототип платформы разработки, CLI, docs, ADR, service manifest, task library, showcases. |
| Encrypted secrets reference | 63 | Внешний reference для GitOps-секретов и CRD/controller модели. |
| Usage metrics gateway prototype | 55 | Прототип gateway для usage metrics, токенов доступа, версионирования API, очередей и биллингового pipeline. |
| UI validation prototype | 25 | Прототип реактивной валидации UI/форм и правил клиентского ввода. |
| VM image factory prototype | 20 | Прототип воспроизводимой сборки VM-шаблонов, hardening, cloud-init, serial console, crash dump. |
| UI composition prototype | 13 | Прототип UI-bootstrap/provider-модели для переносимых frontend-компонентов. |
| Stateful DNS/database operations history | 1 в default branch, больше в development branch | История stateful-инфраструктуры: Postgres/DNS, HA, backup, audit, Terraform/Ansible. |

Найдены git-репозитории в нескольких legacy-прототипах.
Один sandbox-репозиторий не содержал полезной истории.
Главный legacy platform prototype не является git-репозиторием в текущем
дереве, но содержит архитектурную память в docs, ADR, CLI, library-коде и
showcases.

Важно: текущий анализ является product-signal synthesis с targeted current-tree
reads, history-focused scans and agent review. Он не заявляет полный
line-by-line audit каждого исходного файла или полноценный secret/vulnerability
scan. Для такого заявления требуется coverage manifest по source class, all-refs
history treatment and explicit exclusions, как описано в
[26-source-coverage-and-completion-audit.md](26-source-coverage-and-completion-audit.md).

## Что Извлечено Из PDF

PDF задает стратегическую рамку:

- CloudRING как распределенная open/post-cloud платформа.
- Разделение бизнеса провайдера и технологического слоя.
- Open Cloud Standard как общий контракт.
- Service Connector как механизм подключения сервисов к контракту.
- Федерация провайдеров, private cloud, edge, ISV и разработчиков.
- Единый portal/API/marketplace.
- Снижение vendor lock-in, jurisdiction lock-in и trust risk.
- Возможность private/on-prem/edge/disconnected сценариев.
- Revenue sharing, support, enterprise extensions и модель, в которой
  функциональность не исчезает при окончании лицензии.

## Что Извлечено Из Legacy Platform Prototype

Главные уроки:

- Сервисный манифест должен быть источником истины о сервисе.
- Сервис должен объявлять имя, окружения, компоненты, задачи и документацию.
- Локальная разработка должна воспроизводить зависимости сервиса.
- Задачи должны быть переносимыми между локальной машиной и CI.
- Платформа должна генерировать производные runtime-артефакты, а не требовать
  хранить инфраструктурную механику внутри сервиса.
- Платформа должна поддерживать режим отладки зависимостей отдельно от самого
  приложения.
- Документация сервиса должна быть частью lifecycle.
- Плагины нужны для специфичных сценариев, которые не должны попадать в ядро.
- Расширяемость не должна привязывать разработчика к одному языку.
- Архитектурные решения должны фиксироваться через ADR.
- Единое время, единые шаблоны сервиса, observability и стандартизированная
  сборка снижают сложность микросервисной платформы.

## Что Извлечено Из Git Истории

История `metricsgate` показала:

- Важность версионирования API и deprecated-путей.
- Важность idempotency/retry-safe для usage ingestion.
- Важность валидации периодов, единиц измерения, usage и метаданных.
- Важность токенов доступа, доступа по продуктам и фоновой синхронизации прав.
- Важность трассировки, логирования, метрик и понятных ошибок.
- Важность интеграционных тестов и тегированных релизов.

История VM-template проекта показала:

- Сборка образов должна быть воспроизводимой и запускаться через CI.
- В образах нужны serial console, crash dump, cloud-init, growpart,
  VM tools, hardening и cleanup.
- Pipeline и зависимости ролей сами являются продуктовой частью платформы.

История stateful/DNS/Postgres проекта показала:

- Stateful-сервисы требуют HA, реплик, backup, WAL-архивирования, аудита,
  журналирования, Terraform/Ansible трассировки и планов восстановления.
- DNS и база данных являются инфраструктурными сервисами платформы, а не
  случайными side-проектами.

История UI-прототипов показала:

- UI-компоненты должны иметь контракт подключения, typed props/options,
  поддержку CSS-модулей и обновляемую шаблонную библиотеку.
- Валидация должна иметь явные правила, типы ошибок и разные моменты проверки:
  reactive, blur, submit.

## Что Не Переносится В Требования

Запрещено переносить:

- Название конкретной компании-пилота.
- Внутренние URL, домены, IP-адреса, hostnames и имена стендов.
- Пароли, ключи, токены, deploy keys и секретные переменные.
- Длинные фрагменты исходных текстов, конфигураций, документации или коммитов.
- Прямые инструкции, которые воспроизводят внутреннюю инфраструктуру источника.
- Vendor-код как авторское требование CloudRING.

Допустимо переносить:

- Обезличенный сценарий.
- Продуктовую боль.
- Контрактную необходимость.
- Операционный урок.
- Критерии приемки будущей платформы.

## Пробелы После Этого Этапа

Нужно дополнить будущими источниками:

- Формальное принятие Open Cloud Standard schema format через ADR и заполненные
  examples на основе templates.
- Governance федерации.
- Юридическую модель jurisdiction lock и data residency.
- SLA/SLO и границы ответственности.
- Модель сертификации marketplace-сервисов.
- Полную модель settlement, налогов, возвратов и multi-provider invoices.
- Threat model для федерации, private install, edge и disconnected режимов.
- Совместимость обновлений для private/edge-инсталляций.
- Расширенный корпус role scenario fixtures для всех stages, roles and
  negative stop-condition cases.
