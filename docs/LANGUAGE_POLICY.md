# LANGUAGE POLICY

## Purpose

ATLAS by EWU supports users across Europe and must open in a language the user can understand.

Language handling separates the interface language from the conversation language.

## Supported Languages

- `pl` - Polski
- `uk` - Українська
- `ru` - Русский
- `en` - English
- `de` - Deutsch
- `es` - Español
- `pt` - Português

Default language: `pl`.

## UI Language

`uiLanguage` controls visible interface text:

- navigation;
- buttons;
- dashboard labels;
- cards;
- empty states;
- footer;
- errors.

Initial UI language is detected in this order:

1. URL language prefix, for example `/pl`, `/uk`, `/ru`
2. URL query parameter, for example `?lang=de`
3. Saved language from `localStorage` or future user profile
4. Browser/device language
5. Default language: `pl`

URL language overrides saved language because it is an explicit navigation choice.

## Conversation Language

`conversationLanguage` controls the language ATLAS should use in chat replies.

It may differ from `uiLanguage`.

Example:

- User opens `/pl`
- UI language remains Polish
- User writes in Russian
- Conversation language may become Russian
- ATLAS can reply in Russian while UI remains Polish

## Language Switcher

The language switcher must:

- be visible but unobtrusive;
- show the current language name;
- not rely only on flags;
- save manual language choice to `localStorage`;
- not erase chat data;
- not erase dashboard data.

## Adding A New Language

Do not add new languages directly in UI code.

To add a language later:

1. Add it to `configs/languages/languages.json`.
2. Add a translation file in `configs/languages/{code}.json`.
3. Add it to `core/languages.py`.
4. Add detection rules only if needed.
5. Verify all required i18n keys exist.

## Unknown Language

If language cannot be detected from URL, saved setting or browser, ATLAS uses default language `pl`.

No blocking language wall is required at this stage.
