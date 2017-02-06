# ADR-0007 - Marketplace Certification Levels

```yaml
id: ADR-0007
status: proposed
title: Marketplace Certification Levels
context: CloudRING service store должен позволять устанавливать сторонние и внутренние сервисы в private cloud, не заставляя пользователя угадывать их совместимость, безопасность и переносимость.
decision: Каждый service/store item получает certification level и readiness report, где явно указаны supported environments, checks, limitations, responsibilities и next-level gaps.
supersedes: []
requirements:
  - CR-FED-011..018
  - CR-OCS-014..016
  - CR-SELF-017..020
  - CR-MKT-001..019
  - CR-METRIC-011..015
```

## Контекст

Marketplace без сертификации превращается в каталог надежд. Пользователь видит
красивую карточку, но не знает, можно ли сервис ставить в private cloud,
работает ли он offline, как он обновляется, какие данные обрабатывает, где
границы ответственности и что будет при проблеме.

Stage 3 должен ввести app-store опыт для private cloud, но не обязан сразу
делать глобальную federation-коммерцию. Поэтому certification levels нужны
уже сейчас, а settlement и public provider economics могут появиться позже.

## Решение

CloudRING использует уровни сертификации:

- `dev-ready`: сервис пригоден для разработки и тестовой установки;
- `private-ready`: сервис можно устанавливать в private presence при
  выполнении указанных policy и resource requirements;
- `disconnected-ready`: сервис имеет offline/limited-connectivity behavior,
  update и entitlement semantics;
- `edge-ready`: сервис подходит для ограниченных ресурсов, latency/geography
  constraints и delayed sync;
- `public-ready`: сервис готов к публичному provider offering;
- `federation-ready`: сервис готов к cross-provider listing, usage, support и
  policy sync;
- `compliance-ready`: сервис прошел профильный набор security/compliance
  checks для конкретного рынка или класса клиента.

Certification level является install/update gate. Если уровень не подходит
текущей presence, policy или mode, store должен блокировать действие или
требовать explicit override с audit, если override допустим политикой.

Каждый уровень является не маркетинговым бейджем, а readiness report:

- какие checks пройдены;
- какие checks не применимы и почему;
- какие ограничения видны buyer/admin до установки;
- какие responsibilities несут CloudRING, provider, ISV, owner и buyer;
- какие действия нужны для перехода на следующий уровень.

## Почему

CloudRING должен стимулировать экосистему, но пользователь не должен платить
операционным риском за открытость. Certification levels дают безопасный путь
от developer service к private store, public provider и federation без
переписывания продуктового контракта.

## Последствия

Положительные:

- покупатель понимает риск до установки;
- ISV видит понятный путь публикации;
- private cloud может принимать сервисы без ручной экспертизы каждого случая;
- marketplace quality становится измеримой.

Отрицательные:

- сертификация требует времени и tooling;
- некоторые сервисы будут видны, но ограничены по environment;
- уровень сертификации должен обновляться при изменениях сервиса.

Follow-up:

- определить минимальный `private-ready` profile для Stage 3;
- связать certification checks с Open Cloud Standard conformance;
- добавить trust score как производный сигнал, а не замену certification;
- описать suspension/warning flow для нарушений.

## Критерии Приемки

- Service store item показывает certification level и readiness report.
- Сервис нельзя установить в environment, который не входит в compatibility
  profile, без explicit override и audit.
- Update блокируется или требует approval, если новая версия снижает
  certification level ниже policy threshold.
- `private-ready` требует manifest validation, dependency declaration,
  observability, security baseline, update policy и portability statement.
- Buyer/admin видит known limitations до install.
- Failed certification check возвращает actionable remediation для seller.
