# Security Hardening Review: RAGFlow runtime minimization

## Evidence Basis

Мы проверили исходный runtime v1.0.0-rc3, обнаружили рабочий Python3.12 внутри Vim и по запросу пользователя удалили ненужные для текущего document workload пакеты. Приложение не пересобиралось: Go binary SHA256 совпадает с исходным. [Verification snapshot](evidence/verification.json) содержит image IDs/digests, размеры, health и хэши изменённых файлов.

## Constraints

Мы сохранили текущий startup, shell entrypoint, curl healthcheck, парсеры, модели, шрифты, порт18080, сети и все исходные volumes. Это целевое уменьшение runtime, а не shell-less/distroless image. Essential perl-base, bash/dash и package management остаются.

## Opportunity Portfolio

Новая архитектурная переработка для этой задачи не нужна: мы выбрали локальное удаление восьми проверенных пакетов. Разделение ролей/сетей остаётся отдельной работой, без изменений в этой итерации.

## Recommendation Summary

Изменение внедрено: lab Compose использует локальный образ по digest, построенный из прежнего pinned base без сетевых загрузок. Удалены vim/vim-common/vim-runtime, unzip, iproute2 и три пакета libpython3.12. Все слои объединены; удалённые файлы не сохранены в нижних слоях производного образа.

Podman reported size: 777475550 → 705804234 байт, уменьшение71671316 байт (9.22%). Пакеты141 →133. Изолированный стек и рабочая лаба успешно выполнили upload/parse/retrieve/download для TXT/DOCX/PDF; все три формата дали по одному chunk и нашлись по маркеру. [Изолированная проверка](evidence/smoke-results.json), [проверка рабочей лабы](evidence/lab-results.json). В обоих случаях fixtures удалены; временный стек и его volumes удалены.

Исходные таблицы сохранили счётчики:3 datasets,1356 документов,2 пользователя. Это проверка counts, не полное сравнение всех байтов. Векторный путь с реальной embedding-моделью не перепроверялся: существующий model endpoint был выключен. Проверен реальный BM25/full-text путь, без fake embedding service. Шесть остальных сервисов не менялись.

## Next Decisions

Рабочий UI остаётся http://127.0.0.1:18080/. Откат описан в README лабы; исходный image сохранён, конфигурация и приватный backup БД находятся только в lab backup directory. F01/F02 этим изменением не исправлены. Следующее уменьшение runtime до отсутствия всех shell/интерпретаторов потребует отдельной переработки entrypoint/ролей.

[План и критерии внедрения](implementation/minimal-runtime.md).
