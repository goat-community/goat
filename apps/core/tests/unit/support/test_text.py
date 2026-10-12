import pytest
from core.support.text import clean_subject, plain_text_to_html, technical_block


@pytest.mark.unit
def test_escapes_everything() -> None:
    assert plain_text_to_html("<b>bold</b> & 'q' \"d\"") == (
        "<p>&lt;b&gt;bold&lt;/b&gt; &amp; &#x27;q&#x27; &quot;d&quot;</p>"
    )


@pytest.mark.unit
def test_paragraphs_and_line_breaks() -> None:
    text = "Hallo,\n\ndas ist Zeile eins.\nZeile zwei.\r\n\r\n\nGruss"
    assert plain_text_to_html(text) == (
        "<p>Hallo,</p><p>das ist Zeile eins.<br>Zeile zwei.</p><p>Gruss</p>"
    )


@pytest.mark.unit
def test_empty_text_is_empty_html() -> None:
    assert plain_text_to_html("   \n\n ") == ""


@pytest.mark.unit
def test_subject_is_single_line_plain_text() -> None:
    assert (
        clean_subject("  Isochrone\tfails\n<b>now</b>  ")
        == "Isochrone fails <b>now</b>"
    )
    assert len(clean_subject("x" * 500)) == 200


@pytest.mark.unit
def test_technical_block_escapes_values() -> None:
    html = technical_block({"GOAT version": "3.0.1", "Page": "/map/<x>"})
    assert html.startswith("<p><strong>Technical details</strong></p><ul>")
    assert "<li>GOAT version: 3.0.1</li>" in html
    assert "<li>Page: /map/&lt;x&gt;</li>" in html


@pytest.mark.unit
def test_technical_block_empty() -> None:
    assert technical_block({}) == ""
