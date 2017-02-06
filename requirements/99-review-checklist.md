# Review Checklist

Этот checklist запускать после каждой итерации `requirements`.

## Обязательные Проверки

1. Нет конкретной пилотной компании, внутренних доменов, IP, URL, email,
   абсолютных локальных путей, токенов, ключей и секретов.
2. Нет длинных цитат из исходных документов или кода.
3. Новые требования имеют `why`.
4. Ключевые требования имеют acceptance criteria или явно остаются `draft`.
5. Технологии указаны как capability или example/source signal, а не как
   вечный lock-in.
6. Новые требования связаны с bounded context, stage, metric или ADR.
7. Если появился конфликт требований, создан ADR/backlog item.
8. Если источник содержит секреты или внутренние имена, они не перенесены.
9. Если изменение source-derived, обновлен coverage manifest или явно записано,
   почему coverage не меняется.
10. Нет claims полного source/history анализа без coverage manifest.

## Suggested Commands

Запускать из корня проекта:

### Source-Safety Scope

`requirements/` является publishable requirements corpus. Workspace files outside
`requirements/` may be raw source notes, local inventory or operator scratch and
must not be treated as CloudRING specification until the same source-safety gate
is applied. Any public/exportable artifact should include only the checked
requirements corpus or explicitly pass an equivalent scan.

Keep exact private denylist terms in a local ignored scan rule file, not inside
requirements. The checklist stores only redacted classes.

### Private Marker Classes

```powershell
$denylist = Get-Content .local/private-marker-denylist.regex
rg -n --glob '!99-review-checklist.md' $denylist requirements
```

Ожидаемый результат: нет совпадений.

Minimum denylist classes:

- pilot/customer/company names and abbreviations;
- internal domains, hostnames, URLs and email addresses;
- network addresses and topology identifiers;
- absolute local paths and source-bundle paths;
- secret-store, credential, token, key and private-key markers;
- generated logs, runtime state, infrastructure state and grant-like artifacts;
- mojibake or corrupted encoding markers.

Проверка потенциальных секретных слов:

```powershell
rg -n --glob '!99-review-checklist.md' "password|secret|token|private key|ssh key|api key" requirements
```

Ожидаемый результат: совпадения допустимы только в требованиях о secret
management, без конкретных значений.

Проверка ссылок на старые traceability-файлы:

```powershell
rg -n --glob '!99-review-checklist.md' "<deprecated-traceability-name>|<absolute-local-path>|<raw-source-bundle-path>" requirements
```

Ожидаемый результат: нет совпадений.

Проверка объема и файлов:

```powershell
Get-ChildItem requirements -Recurse -File -Filter *.md | Select-Object FullName,Length | Sort-Object FullName
Get-ChildItem requirements -Recurse -File -Filter *.md | ForEach-Object { Get-Content -Encoding UTF8 $_.FullName } | Measure-Object -Line -Word -Character
```

## Review Questions

- Можно ли по этим требованиям реализовать capability без доступа к source?
- Понятно ли, почему требование существует?
- Не заставляет ли требование использовать старую технологию без причины?
- Есть ли способ проверить выполнение?
- Может ли AI-агент понять scope, риск и validation?
- Снижает ли требование lock-in или хотя бы не увеличивает его?
- Сохраняет ли требование простоту опыта пользователя?
- Не заявляет ли итерация больше coverage, чем реально доказано?
