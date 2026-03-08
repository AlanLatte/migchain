"""RichPresenter.prompt_scaffold -- интерактивный ввод параметров миграции.

- тип "domain" запрашивает только имя домена
- тип "table" с существующими поддиректориями показывает выбор
- тип "inserter" с ручным вводом домена
- тип "freeform" с ручным вводом поддиректории
"""
# pylint: disable=protected-access

from unittest.mock import MagicMock, patch

from migchain.presentation.console import RichPresenter


class _FakePrompt:
    """Имитация InquirerPy prompt с настраиваемым результатом."""

    def __init__(self, value):
        self._value = value

    def execute(self):
        return self._value


def _make_inquirer_mock(responses):
    """Создает мок inquirer, возвращающий ответы по очереди."""
    mock = MagicMock()
    select_responses = []
    text_responses = []

    for resp in responses:
        if resp["type"] == "select":
            select_responses.append(_FakePrompt(resp["value"]))
        elif resp["type"] == "text":
            text_responses.append(_FakePrompt(resp["value"]))

    mock.select.side_effect = select_responses
    mock.text.side_effect = text_responses
    return mock


class TestScaffoldDomain:
    """Защищает контракт создания доменной миграции."""

    def test_domain_type_returns_domain_request(self):
        """Защищает от потери маршрута scaffold_type='domain'."""
        inquirer_mock = _make_inquirer_mock(
            [
                {"type": "select", "value": "domain"},
                {"type": "text", "value": "orders"},
            ],
        )

        presenter = RichPresenter()
        with patch("migchain.presentation.console.inquirer", inquirer_mock):
            result = presenter.prompt_scaffold([], {})

        assert result.scaffold_type == "domain"
        assert result.domain == "orders"


class TestScaffoldTableWithSubdirs:
    """Защищает контракт выбора поддиректории из существующих."""

    def test_table_with_existing_subdirs_selects_subdir(self):
        """Защищает от потери выбора существующей поддиректории."""
        inquirer_mock = _make_inquirer_mock(
            [
                {"type": "select", "value": "table"},
                {"type": "select", "value": "users"},
                {"type": "select", "value": "roles"},
            ],
        )

        text_mock = _FakePrompt("add-index")
        inquirer_mock.text.side_effect = [text_mock]

        presenter = RichPresenter()
        with patch("migchain.presentation.console.inquirer", inquirer_mock):
            result = presenter.prompt_scaffold(
                ["users", "orders"],
                {"users": ["roles", "permissions"]},
            )

        assert result.scaffold_type == "table"
        assert result.domain == "users"
        assert result.subdirectory == "roles"
        assert result.description == "add-index"


class TestScaffoldInserterManualDomain:
    """Защищает контракт ручного ввода домена при выборе '(enter manually)'."""

    def test_inserter_with_manual_domain_entry(self):
        """Защищает от потери маршрута ручного ввода имени домена."""
        inquirer_mock = _make_inquirer_mock(
            [
                {"type": "select", "value": "inserter"},
                {"type": "select", "value": "(enter manually)"},
            ],
        )

        inquirer_mock.text.side_effect = [
            _FakePrompt("custom_domain"),
            _FakePrompt("subdir_name"),
            _FakePrompt("insert-data"),
        ]

        presenter = RichPresenter()
        with patch("migchain.presentation.console.inquirer", inquirer_mock):
            result = presenter.prompt_scaffold(
                ["users"],
                {},
            )

        assert result.scaffold_type == "inserter"
        assert result.domain == "custom_domain"
        assert result.subdirectory == "subdir_name"
        assert result.description == "insert-data"


class TestScaffoldFreeformManualSubdir:
    """Защищает контракт ручного ввода поддиректории через '(enter manually)'."""

    def test_freeform_with_manual_subdirectory(self):
        """Защищает от потери маршрута ручного ввода поддиректории."""
        inquirer_mock = _make_inquirer_mock(
            [
                {"type": "select", "value": "freeform"},
                {"type": "select", "value": "users"},
                {"type": "select", "value": "(enter manually)"},
            ],
        )

        inquirer_mock.text.side_effect = [
            _FakePrompt("custom_subdir"),
            _FakePrompt("add-trigger"),
        ]

        presenter = RichPresenter()
        with patch("migchain.presentation.console.inquirer", inquirer_mock):
            result = presenter.prompt_scaffold(
                ["users", "orders"],
                {"users": ["roles"]},
            )

        assert result.scaffold_type == "freeform"
        assert result.domain == "users"
        assert result.subdirectory == "custom_subdir"
        assert result.description == "add-trigger"


class TestScaffoldRootSubdir:
    """Защищает контракт выбора '(root)' как поддиректории."""

    def test_root_subdir_produces_empty_subdirectory(self):
        """Защищает от ошибки при выборе (root) -- subdirectory должен быть пустым."""
        inquirer_mock = _make_inquirer_mock(
            [
                {"type": "select", "value": "table"},
                {"type": "select", "value": "users"},
                {"type": "select", "value": "(root)"},
            ],
        )

        inquirer_mock.text.side_effect = [_FakePrompt("create-table")]

        presenter = RichPresenter()
        with patch("migchain.presentation.console.inquirer", inquirer_mock):
            result = presenter.prompt_scaffold(
                ["users"],
                {"users": ["roles"]},
            )

        assert result.subdirectory == ""
