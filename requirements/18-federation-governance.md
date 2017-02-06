# Federation Governance

Federation governance определяет, как CloudRING остается открытой сетью, но не
теряет качество, безопасность и совместимость.

## Участники

| Role | Права | Обязанности |
|---|---|---|
| Public Provider | Предоставляет публичное presence и продает сервисы. | Соблюдать стандарт, публиковать SLA/pricing/capacity, отдавать usage/audit. |
| Private Cloud Participant | Подключает private-инсталляцию к сети или marketplace. | Соблюдать policy exchange, защищать данные, синхронизировать разрешенные события. |
| Edge Operator | Предоставляет edge presence. | Поддерживать connected/disconnected режимы и delayed sync. |
| ISV | Публикует сервисы. | Проходить certification, поддерживать lifecycle, billing и support terms. |
| Reseller/Integrator | Продает или внедряет сервисы. | Не искажать условия, support handoff и billing chain. |
| Governance Operator | Поддерживает правила federation. | Не превращать governance в централизованный lock-in. |

## Participant Identity

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-001 | Каждый участник federation должен иметь cryptographic identity и organization profile. | Нужна проверяемая принадлежность событий и обязательств. |
| CR-FEDGOV-002 | Identity должна поддерживать delegation: provider admin, billing agent, support agent, automation, AI-agent. | Участник не является одним пользователем. |
| CR-FEDGOV-003 | Участник должен публиковать trust metadata: jurisdiction, legal entity class, supported compliance profiles, contact/support channels. | Пользователь и policy engine должны учитывать не только технические параметры. |
| CR-FEDGOV-004 | Identity участника должна иметь lifecycle: candidate, active, suspended, retired, revoked. | Участников нужно подключать и отключать управляемо. |

## Trust Anchors

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-005 | Federation должна иметь trust anchors для подписи participant metadata, service certification и settlement messages. | Без подписей нельзя доверять cross-provider данным. |
| CR-FEDGOV-006 | Trust anchors должны быть заменяемыми и распределенными по governance policy. | Один корневой центр не должен стать новым lock-in. |
| CR-FEDGOV-007 | Участник должен уметь проверить authenticity federation messages offline, если работает disconnected. | Edge/private сценарии не всегда online. |

## Conformance Levels

| Level | Смысл |
|---|---|
| `developer` | Сервис или presence пригоден для разработки и тестов. |
| `private-ready` | Можно использовать в private-инсталляции с локальной ответственностью. |
| `public-ready` | Можно продавать пользователям public provider. |
| `federation-ready` | Можно публиковать через federation catalog и settlement. |
| `edge-ready` | Поддерживает resource limits, delayed sync и disconnected constraints. |
| `regulated-ready` | Поддерживает заявленный compliance/data residency profile. |

Требования:

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-008 | Conformance level должен быть machine-readable и отображаться buyer/admin/agent. | Решения должны быть автоматизируемы. |
| CR-FEDGOV-009 | Уровень conformance должен иметь тесты и evidence. | Сертификация без доказательств не создает доверия. |
| CR-FEDGOV-010 | Понижение conformance должно автоматически влиять на marketplace availability. | Нельзя продолжать продавать сервис как совместимый после деградации. |

## Scoped Data Sharing

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-011 | Участник должен делиться только минимально необходимыми metadata для catalog, placement, billing, support и audit. | Федерация не должна требовать раскрытия всей внутренней инфраструктуры. |
| CR-FEDGOV-012 | Data sharing scopes должны быть явно связаны с purpose. | Нельзя переиспользовать данные вне заявленной цели. |
| CR-FEDGOV-013 | Пользователь должен видеть, какие участники получают metadata его сервиса. | Cross-provider trust требует прозрачности. |
| CR-FEDGOV-014 | Sensitive operational data должна агрегироваться или редактироваться до federation exchange, если детализация не обязательна. | Участники не должны утекать внутренней topology. |

## Suspension And Revocation

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-015 | Governance должен поддерживать suspension участника, сервиса, offer или capability. | Нарушения совместимости или безопасности нужно быстро останавливать. |
| CR-FEDGOV-016 | Suspension должен иметь reason, scope, start time, appeal path и remediation requirements. | Участник должен понимать, как восстановиться. |
| CR-FEDGOV-017 | Suspension не должен автоматически уничтожать данные клиентов. | Безопасность не должна превращаться в потерю контроля. |
| CR-FEDGOV-018 | Revocation trust keys должна иметь emergency flow и propagation strategy. | Компрометация ключа требует быстрого действия. |

## Disputes

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-019 | Federation должна поддерживать disputes по usage, settlement, SLA, certification и policy violation. | В сети независимых участников споры неизбежны. |
| CR-FEDGOV-020 | Dispute должен иметь evidence bundle: events, signatures, policy decisions, usage records, support timeline. | Решение спора должно быть доказуемым. |
| CR-FEDGOV-021 | Dispute process не должен блокировать unrelated services пользователя. | Один спор не должен ломать всю инфраструктуру. |

## Fork And Compatibility Policy

| ID | Требование | Почему |
|---|---|---|
| CR-FEDGOV-022 | Open Cloud Standard должен допускать forks/extensions, но требовать compatibility declaration. | Инновации нельзя запрещать, но несовместимость должна быть видимой. |
| CR-FEDGOV-023 | Extension не должен называться compatible, если ломает mandatory contract. | Иначе federation потеряет смысл. |
| CR-FEDGOV-024 | Участник может работать вне federation governance, но такие сервисы должны маркироваться как non-federated. | Свобода не должна вводить пользователя в заблуждение. |

