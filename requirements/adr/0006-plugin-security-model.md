# ADR-0006 - Plugin Security Model

```yaml
id: ADR-0006
status: proposed
title: Plugin Security Model
context: CloudRING должен расширяться enterprise/private/integration плагинами, но исполняемое расширение является trust boundary и не должно превращаться в скрытый root-доступ.
decision: Плагины допускаются только через declared capability, explicit permissions, signed/verified package identity, sandbox or constrained execution profile, audit и revocation path.
supersedes: []
requirements:
  - CR-DX-020..024
  - CR-SEC-025..027
  - CR-APPROVAL-001..008
  - CR-OCS-028..032
```

## Контекст

CloudRING должен быть расширяемым: разные private-инсталляции, enterprise
процессы, провайдеры, ISV и AI-агенты будут приносить специфичные интеграции.
Если каждую интеграцию встраивать в ядро, платформа станет тяжелой и медленной.
Если разрешить произвольные плагины без модели безопасности, service store
станет каналом компрометации.

Плагин может читать состояние, менять конфигурацию, запускать проверки,
подключать внешние системы, публиковать UI или выполнять lifecycle hooks.
Поэтому он должен рассматриваться как продуктовая capability с явными
границами, а не как произвольный скрипт.

## Решение

CloudRING использует permissioned plugin model:

- каждый plugin package имеет identity, version, publisher, compatibility
  profile и declared capabilities;
- plugin не получает доступ к платформе без explicit permission grant;
- permissions должны быть scoped по presence, service, project, environment и
  operation class;
- plugin actions проходят через approval matrix так же, как agent actions;
- plugin package должен иметь проверяемое происхождение и integrity evidence;
- plugin имеет trust state: candidate, verified, warning, suspended, revoked;
- plugin должен иметь audit trail: кто установил, кто разрешил, какие действия
  выполнены и какой результат получен;
- plugin можно отключить, отозвать или изолировать без удаления всей платформы;
- plugin UI и automation не обходят Open Cloud Standard, policy engine и secret
  broker.

## Почему

Расширяемость нужна, чтобы CloudRING не устаревал и мог адаптироваться к
разным компаниям, рынкам и инфраструктурам. Но исполняемое расширение является
границей доверия. Без строгой модели permissions расширяемость станет новым
источником lock-in и операционного риска.

## Последствия

Положительные:

- private и enterprise сценарии могут добавлять интеграции без изменения ядра;
- service store может публиковать extensions с понятным trust profile;
- администратор видит риск плагина до установки;
- AI-агенты могут проверять plugin permissions до действия.

Отрицательные:

- публикация плагина требует conformance и security evidence;
- некоторые быстрые автоматизации лучше оставлять task library, а не plugin;
- потребуются UX и policy для объяснения permissions.

Follow-up:

- определить plugin certification checks для Stage 3;
- описать plugin install/update/remove lifecycle;
- связать plugin permissions с service connector и embedded UI contracts;
- добавить marketplace warning для overly broad permissions.

## Критерии Приемки

- Plugin listing показывает identity, publisher, permissions, compatibility,
  risks и support/update terms.
- Plugin не устанавливается без declared capabilities и permission review.
- Plugin actions создают audit events с actor, scope, risk class и result.
- Plugin не получает plaintext secrets, если доступ может идти через brokered
  capability.
- Plugin можно disable/revoke с понятным impact report.
- Критичный security, policy или compatibility incident переводит plugin в
  warning/suspended/revoked state и блокирует новые risky actions до review.
