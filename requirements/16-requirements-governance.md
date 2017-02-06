# Requirements Governance

Эта папка должна жить годами.
Чтобы она оставалась полезной, требования должны иметь статус, владельца смысла,
историю изменений и правила разрешения конфликтов.

## Статусы Требований

| Статус | Смысл |
|---|---|
| `draft` | Требование сформулировано, но требует проверки или источников. |
| `accepted` | Требование принято как часть продуктовой модели CloudRING. |
| `experimental` | Требование нужно проверить прототипом или research spike. |
| `superseded` | Требование заменено новым, но сохранено для истории. |
| `rejected` | Требование осознанно отклонено с причиной. |
| `deprecated` | Требование было верным, но выводится из будущей модели. |

## Правила Добавления Источника

| ID | Правило | Почему |
|---|---|---|
| CR-GOV-001 | Каждый новый источник должен быть зарегистрирован в source analysis. | Иначе теряется происхождение требований. |
| CR-GOV-002 | Источник анализируется полностью или с явным списком исключений. | Частичный анализ создает ложную уверенность. |
| CR-GOV-003 | Из источника переносятся только смысл, сценарии, причины и acceptance criteria. | Это защищает от copyright и от копирования устаревшей реализации. |
| CR-GOV-004 | Перед записью нужно удалить внутренние имена, URLs, IP, секреты и пилотный контекст. | Requirements должны быть переносимыми и безопасными. |
| CR-GOV-005 | Если источник противоречит существующим требованиям, создается conflict note или ADR. | Конфликт нельзя решать молча. |

## Правила Изменения Требования

| ID | Правило | Почему |
|---|---|---|
| CR-GOV-006 | Нельзя удалять accepted requirement без superseding/rejected записи. | История решений важна для будущих агентов. |
| CR-GOV-007 | Изменение `why` требует особенно внимательной проверки. | Изменение причины может поменять архитектуру. |
| CR-GOV-008 | Если изменилась технология, но причина прежняя, нужно обновлять implementation guidance, а не продуктовый requirement. | Контракт должен жить дольше реализации. |
| CR-GOV-009 | Если requirement стал слишком большим, его нужно разбить на несколько атомарных требований. | Агенты плохо реализуют расплывчатые требования. |
| CR-GOV-010 | Если requirement не имеет acceptance criteria, он остается draft. | Непроверяемое требование нельзя считать принятым. |

## Правила Continuous Evolution

| ID | Правило | Почему |
|---|---|---|
| CR-GOV-011 | Incident, support case, conformance failure, security finding, technology change and ecosystem feedback должны рассматриваться как source signals. | Платформа учится не только из документов. |
| CR-GOV-012 | Повторяющийся signal должен создать requirement, ADR, runbook, conformance check, agent task или explicit rejection. | Повторение является доказательством системного урока. |
| CR-GOV-013 | Technology refresh требует product contract impact analysis. | Новая технология не должна незаметно менять миссию и обещания. |
| CR-GOV-014 | Accepted testable requirement должен иметь validation path или documented exception. | Иначе conformance не защищает продукт. |
| CR-GOV-015 | Conformance exception должен иметь owner, reason, scope and review trigger. | Исключения без срока становятся скрытым стандартом. |
| CR-GOV-016 | AI-generated evolution proposal остается draft до validation and approval rules. | Агент не должен сам принимать продуктовые trade-offs. |
| CR-GOV-017 | Rejected/deferred proposal должен сохранять reason and reconsideration conditions. | Будущие агенты должны понимать, почему путь не выбран. |
| CR-GOV-018 | Source-derived evolution changes проходят anonymization and copyright-safe paraphrase checks. | Learning loop не должен переносить внутренние имена, секреты или копии источников. |
| CR-GOV-019 | Operational lesson должен быть классифицирован как no-change, implementation guidance, conformance update, requirement change, ADR, runbook, agent task or rejection. | Не каждый урок должен менять продуктовый контракт. |
| CR-GOV-020 | Conformance changes должны быть versioned with reason, affected scope and compatibility impact. | Проверки являются контрактом между участниками. |
| CR-GOV-021 | Failed implementation не может ослабить conformance без ADR/conflict note. | Реализация не должна молча переписывать стандарт. |
| CR-GOV-022 | Evolution item закрывается только через accepted artifact, validation, rejection/defer reason or owner-approved exception. | Closure must prove learning outcome. |
| CR-GOV-023 | Source intake must include coverage manifest before completeness claims. | Полный анализ нельзя заявлять без доказательства покрытия. |
| CR-GOV-024 | Partial source analysis must create explicit follow-up pass or accepted exclusion. | Sampling полезен, но должен оставлять видимый хвост. |
| CR-GOV-025 | History analysis must state current-tree, all-refs, tags and deleted-path coverage. | Git history может хранить решения, которых нет в текущей ветке. |
| CR-GOV-026 | Completion audit must preserve the original objective scope. | Нельзя объявлять цель выполненной потому, что выполнена удобная часть. |

## Conflict Resolution

Конфликт требований решается в таком порядке:

1. Миссия CloudRING: снижение provider/technology/jurisdiction lock-in.
2. Безопасность и контроль пользователя над данными.
3. Open Cloud Standard и переносимость контрактов.
4. Self-service и agent-operability.
5. Простота продукта.
6. Стоимость реализации.
7. Предпочтения конкретной технологии.

Если два требования конфликтуют, нельзя выбирать только по привычной технологии.
Нужно сформулировать ADR и явно записать tradeoff.

## Quality Gates Для Requirements PR/Change

Любое изменение requirements должно пройти проверку:

- Нет внутренних имен, путей, IP, секретов, URL пилотного контекста.
- Нет длинных цитат из источников.
- Есть `why`.
- Есть acceptance criteria или причина, почему их пока нет.
- Требование не навязывает конкретную технологию без причины.
- Понятно, какую роль пользователя оно обслуживает.
- Понятно, к какому bounded context оно относится.
- Есть связи с другими требованиями или ADR, если применимо.
- Для source-derived changes обновлен coverage manifest или явно записано, почему
  он не меняется.

## Agent Review Checklist

AI-агент, который редактирует requirements, должен в финале сообщить:

1. Какие источники использованы.
2. Какие файлы изменены.
3. Какие требования добавлены/изменены/superseded.
4. Какие решения требуют ADR.
5. Какие проверки обезличивания выполнены.
6. Какие пробелы остались.

## Версионирование Папки

Рекомендуемая схема:

- `requirements iteration` - крупная итерация смысловой базы.
- `source intake` - добавление нового источника.
- `architecture revision` - изменение архитектурной модели.
- `governance revision` - изменение правил управления требованиями.

Каждая итерация должна сохранять backward traceability: почему изменение
появилось и какие старые требования оно изменило.
