# ADR: Выбор архитектуры сервинга на основе Metrics Driven Development

## Status

Accepted

## Context

В проекте нужно принять архитектурное решение не “на глаз”, а на основе метрик. Для этого сравниваются два варианта системы:

1. Existing system.
2. Improved system.

Сравниваемая метрика:

```text
latency
```

Цель: понять, дает ли improved system статистически значимое снижение latency.

## Decision drivers

Решение должно учитывать:

- latency prediction service;
- воспроизводимость deployment;
- возможность healthcheck;
- возможность мониторинга;
- простоту поддержки до устной защиты;
- возможность дальнейшего развития MLOps pipeline.

## Data

Используются два набора данных latency:

```python
existing_system_responses = np.random.normal(loc=3.5, scale=0.4, size=500000)
improved_system_responses = np.random.normal(loc=2.0, scale=0.4, size=500000)
```

Интерпретация:

- existing system имеет среднее время отклика около 3.5 секунд;
- improved system имеет среднее время отклика около 2.0 секунд.

## Hypotheses

H0:

```text
Improved system не снижает latency по сравнению с existing system.
```

H1:

```text
Improved system снижает latency по сравнению с existing system.
```

## Significance level

Уровень значимости:

```text
alpha = 0.05
```

## Statistical test

Выбранный тест:

```text
one-sided Mann-Whitney U test
```

Причина выбора:

- сравниваются две независимые выборки;
- важно проверить, что latency improved system статистически меньше;
- тест не требует строгого предположения о нормальности распределений.

## Analysis and visualization

Код анализа:

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

np.random.seed(42)

existing_system_responses = np.random.normal(loc=3.5, scale=0.4, size=500000)
improved_system_responses = np.random.normal(loc=2.0, scale=0.4, size=500000)

plt.figure(figsize=(10, 6))
sns.kdeplot(existing_system_responses, label="Existing system", fill=True, color="red")
sns.kdeplot(improved_system_responses, label="Improved system", fill=True, color="green")
plt.title("Latency distribution comparison")
plt.xlabel("Response time, seconds")
plt.ylabel("Density")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)
plt.show()

statistic, p_value = mannwhitneyu(
    improved_system_responses,
    existing_system_responses,
    alternative="less",
)

print(f"statistic = {statistic}")
print(f"p_value = {p_value}")

alpha = 0.05

if p_value < alpha:
    print("Reject H0. Improved system has statistically lower latency.")
else:
    print("Fail to reject H0.")
```

## Test result

Если `p_value < 0.05`, H0 отклоняется.

Это означает, что improved system имеет статистически значимо меньшую latency по сравнению с existing system.

## Decision

Решение:

```text
Принять improved serving architecture.
```

В рамках проекта improved architecture реализуется как:

```text
Dockerized FastAPI service on Yandex Cloud VM
```

Аргументация:

1. FastAPI service предоставляет явный REST API.
2. Docker делает deployment воспроизводимым.
3. VM дает реальную облачную ссылку.
4. `/health` позволяет проверять доступность.
5. `/metrics` позволяет отдавать метрики модели и SLO.
6. Docker container можно перезапускать и обновлять при выкладке новой модели.
7. Архитектура поддерживает дальнейшее развитие до blue-green или canary deployment.

Итоговое архитектурное решение:

```text
Использовать Dockerized FastAPI service на Yandex Cloud VM как production-like prediction service.
```

## Consequences

Положительные последствия:

- сервис доступен по публичной ссылке;
- можно показать `/docs`, `/health`, `/metrics`;
- deployment воспроизводится через Docker;
- контейнер можно проверить через `docker ps`;
- архитектура совместима с MLOps maturity level 2.

Ограничения:

- VM нужно поддерживать включенной до устной защиты;
- в этой версии нет полноценного автоматического blue-green deployment;
- переключение модели выполняется через замену артефакта и перезапуск контейнера.

## Links

Связанные документы:

```text
README.md
docs/architecture.md
monitoring/sli_slo.md
