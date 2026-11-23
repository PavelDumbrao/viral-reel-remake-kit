# Инструменты и репозитории: всё, чем сделаны 9 ремейков

Список того, что реально работало 23.11.2026, и чем это заменить, если у вас другой набор. Цены — на ноябрь 2026, проверяйте на сайтах.

## Найти залетевший ролик
| Инструмент | Что делает | Где |
|---|---|---|
| **Контент-хаб клуба Хардкодинг PRO** (MCP) | ищет ролики, у которых просмотров в 3–900 раз больше, чем обычно у автора; проверяет запрос перед поиском (`check_search` → `find_trends`) | доступ участникам клуба по ключу платформы /learn |
| Apify `instagram-hashtag-scraper`, `instagram-reel-scraper` | сбор роликов и медианы автора (то, что под капотом хаба) | https://apify.com |

Без хаба: смотрите Reels по хэштегам ниши и сравнивайте просмотры ролика с обычными у автора (×3 и выше — залетел).

## Скачать образец
| Инструмент | Зачем | Где |
|---|---|---|
| **yt-dlp** | скачать ролик; для Instagram с куками браузера | https://github.com/yt-dlp/yt-dlp · `scripts/download.sh` |
| ffmpeg | вынуть звук, кадры, громкость −14 LUFS | https://ffmpeg.org |

Instagram отдаёт максимум 540×960 — для разбора хватает.

## Разобрать в JSON
| Инструмент | Зачем | Где |
|---|---|---|
| **ElevenLabs Scribe v2** | речь → слова с таймингами (ru, en и ещё 90 языков) | https://elevenlabs.io/docs · `scripts/stt_words.py` |
| **frames_05s.py** | кадр каждые 0,5 с со словом, которое звучит в этот момент, листами | `scripts/frames_05s.py` (нужен ffmpeg и Pillow) |
| Ваш агент (Claude Code, Codex, Antigravity…) | смотрит все листы и пишет `analysis.json` по схеме | `docs/contract.md` |

## Голос
| Инструмент | Зачем | Где |
|---|---|---|
| **ElevenLabs** `eleven_v4_turbo`, `/with-timestamps` | ваш голос-клон + тайминги каждого слова (для титров и рта персонажа) | https://elevenlabs.io · скрипт `tts_timeline.py` в [ai-video-lesson-kit](https://github.com/PavelDumbrao/ai-video-lesson-kit) |
| Pronunciation dictionary ElevenLabs | правильное звучание «Claude», «GitHub», «дашборд» | кабинет ElevenLabs → Pronunciation |

Настройки, которые работали: stability 0.25, similarity 0.8, speaker boost. `speed` у `eleven_v4_turbo` не работает — длину подгоняют `ffmpeg atempo 1.05–1.08`.

## Графика и сборка (видео кодом, без генераторов)
| Инструмент | Зачем | Где |
|---|---|---|
| **HyperFrames** (HeyGen, Apache-2.0) | движок: сцена = HTML + GSAP → MP4, `check`, `snapshot`, `render` | https://github.com/heygen-com/hyperframes · `npm i -g hyperframes` |
| **OpenMotion** (Apache-2.0) | студия поверх HyperFrames: проекты, MCP для агента, Studio для правок, 291 шаблон, экспорт под Reels/Shorts | https://github.com/nexu-io/openmotion |
| Remotion | запасной путь, если привычнее React | https://www.remotion.dev |
| Google Chrome headless | скриншоты «своих» сайтов для каруселей | установлен вместе с HyperFrames |

Шрифты с кириллицей: Inter, Onest, Montserrat, JetBrains Mono (Google Fonts, OFL); курсив с кириллицей — P052 (URW base35) или Cormorant Garamond.

## Нарисованный персонаж (вы в стиле автора)
| Инструмент | Зачем | Где |
|---|---|---|
| **Nano Banana** (Gemini image) | база персонажа по вашему фото + правки: 4–9 ртов, позы рук, моргание | kie.ai или любой шлюз с `nano-banana` |
| Python numpy + Pillow | нарезка на слои и «перекладка» (рот по буквам речи, моргание, позы) | приёмы в `docs/lessons.md` |

## Ваше живое лицо (говорящая голова)
| Инструмент | Зачем | Где |
|---|---|---|
| **Google Omni** у Yiciyuang | 10 с говорящего вас из фото, ≈ 9 ₽ | [omni-video-kit](https://github.com/PavelDumbrao/omni-video-kit) |
| **kie.ai** (Kling Avatar, InfiniTalk, OmniHuman) | говорящее лицо по фото и голосу | [ai-video-lesson-kit](https://github.com/PavelDumbrao/ai-video-lesson-kit) → `skills/face-kie-avatar` |
| ElevenLabs speech-to-speech | заменить голос генератора на ваш | `guides/my-voice.md` в omni-video-kit |

## Рендер
| Где | Когда |
|---|---|
| Локально `hyperframes render` | ролик до 90 с, 5–6 минут |
| Hugging Face Jobs кусками | когда локально долго; инструкция в [ai-video-lesson-kit](https://github.com/PavelDumbrao/ai-video-lesson-kit) → `cloud/` |

## Проверка
| Инструмент | Зачем |
|---|---|
| `frames_05s.py` по готовому ролику | первая линия: смотреть все кадры самому |
| Gemini 3.1 Pro (видео со звуком) | вторая линия: рассинхрон, обрезанные слова, ударения; находки проверять измерением |
| Scribe v2 по готовому ролику | слова голоса = сценарий |
| `ffmpeg loudnorm` | громкость −14 LUFS для Reels |

## Публикация
Без фоновой музыки при сборке: музыку добавляют в самом Instagram / TikTok (охват выше). Автопостинг — [postforme-kit](https://github.com/PavelDumbrao/postforme-kit).
