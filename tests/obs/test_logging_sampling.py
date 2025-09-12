from pathlib import Path

from _pytest.capture import CaptureFixture

from dictdb import logger, configure_logging


def test_console_debug_sampling(capfd: CaptureFixture[str]) -> None:
    configure_logging(level="DEBUG", console=True, logfile=None, sample_debug_every=3)
    for i in range(5):
        logger.bind(test="sampling", i=i).debug("dbg")
    out = capfd.readouterr().out
    # Sampling every 3rd DEBUG; configure_logging emits one DEBUG first,
    # so from our 5 we expect 2 to pass through.
    assert out.count("dbg") == 2


def test_file_debug_sampling(tmp_path: Path) -> None:
    f = tmp_path / "sampled.log"
    configure_logging(
        level="DEBUG", console=False, logfile=str(f), sample_debug_every=2
    )
    for i in range(4):
        logger.bind(test="sampling", i=i).debug("dbg-file")
    content = f.read_text()
    # Expect about half of them (every 2nd)
    assert content.count("dbg-file") == 2
