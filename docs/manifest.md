# ML System Manifest

## Предыстория

В учебном проекте рассматривается задача оценки себестоимости товара по данным о транзакциях велосипедного магазина.

## Ценностное предложение

Сервис помогает автоматически оценивать standard_cost. Это полезно для анализа маржинальности, поиска аномальных транзакций и поддержки ценообразования.

## Цели

1. Подготовить воспроизводимый pipeline обучения модели.
2. Развернуть модель как REST API.
3. Обеспечить healthcheck и базовые метрики сервиса.
4. Сохранять метрики экспериментов.
5. Поддержать возможность переобучения модели.

## Решение

Заявленный уровень зрелости ML-системы: уровень 2.

Компоненты системы:

- GitHub для версионирования кода.
- GitHub Actions для CI.
- Docker и Docker Compose для запуска сервиса.
- FastAPI для model serving.
- MLflow для логирования экспериментов.
- Prefect flow для описания retraining pipeline.
- Endpoint /health для контроля доступности.
- Endpoint /metrics для публикации offline-метрик модели и SLO.

## Осуществимость

Проект реализуется одним разработчиком. Используются Python, scikit-learn, FastAPI, Docker, GitHub Actions и облачная VM.

## Данные

Training dataset: исторические транзакции.

Production input: JSON-запросы к endpoint /predict.

Target: standard_cost.

## Метрики

Бизнес-метрика:

- средняя абсолютная ошибка оценки себестоимости товара.

ML-метрики:

- MAE
- RMSE
- R2

Онлайн-метрики:

- healthcheck status
- latency p95
- error rate

## Оценка качества модели

Качество модели оценивается на отложенной тестовой выборке. Основная метрика: MAE.

## Подбор модели

Используется итеративный подход:

1. Baseline model.
2. RandomForestRegressor.
3. Сравнение по MAE, RMSE и R2.
4. Выбор модели с лучшим балансом качества и простоты эксплуатации.

## Инференс

Тип инференса: real-time inference через REST API.

## Обратная связь

После появления фактического standard_cost для новых транзакций можно сравнивать prediction и actual value. Если MAE превышает заданный SLO, запускается retraining pipeline.

MDD используется: да.

## Управление проектом

Команда: 1 разработчик.

Результаты:

- GitHub repository.
- Рабочий облачный API.
- Dockerized service.
- CI pipeline.
- MLflow experiment logging.
- Prefect retraining pipeline.
- SLI/SLO documentation.
- ADR document for MDD decision.
