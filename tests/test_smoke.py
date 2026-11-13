# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from urllib.parse import quote

import pytest

SOLAN = [sys.executable, "-c", "from solan.core import run; run()"]


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def fetch(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.status, response.read()


@pytest.fixture
def shared(tmp_path):
    (tmp_path / "Foto vacanze").mkdir()
    (tmp_path / "Foto vacanze" / "mare.jpg").write_bytes(b"jpg")
    (tmp_path / "note è.txt").write_text("hello", encoding="utf-8")
    return tmp_path


@pytest.fixture
def server(shared):
    port = free_port()
    proc = subprocess.Popen([*SOLAN, str(shared), "-p", str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            fetch(url)
            break
        except OSError:
            if proc.poll() is not None:
                pytest.fail(f"solan exited: {proc.stdout.read().decode(errors='replace')}")
            time.sleep(0.1)
    yield url, port
    proc.terminate()
    proc.wait(timeout=10)


def test_listing_and_download(server):
    url, _ = server
    status, body = fetch(url + "/")
    page = body.decode("utf-8")
    assert status == 200
    assert "Foto vacanze" in page
    assert "note è.txt" in page

    assert fetch(url + "/" + quote("note è.txt")) == (200, b"hello")
    status, body = fetch(url + "/" + quote("Foto vacanze") + "/")
    assert status == 200 and "mare.jpg" in body.decode("utf-8")


def test_port_already_in_use(server, shared):
    _, port = server
    result = subprocess.run(
        [*SOLAN, str(shared), "-p", str(port)], check=False, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 1
    assert f"Address already in use: port {port}" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.skipif(os.name == "nt", reason="Ctrl+C can't be sent to a single process on Windows")
def test_ctrl_c_stops_cleanly(shared):
    port = free_port()
    proc = subprocess.Popen([*SOLAN, str(shared), "-p", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for _ in range(100):
        try:
            fetch(f"http://127.0.0.1:{port}/")
            break
        except OSError:
            time.sleep(0.1)
    proc.send_signal(signal.SIGINT)
    out, err = proc.communicate(timeout=10)
    assert proc.returncode == 0
    assert b"Stopped" in out
    assert b"Traceback" not in err


@pytest.mark.skipif(not os.environ.get("SOLAN_TEST_NGROK"), reason="downloads ngrok; set SOLAN_TEST_NGROK=1")
def test_ngrok_without_account(shared):
    env = {k: v for k, v in os.environ.items() if k != "NGROK_AUTHTOKEN"}
    result = subprocess.run(
        [*SOLAN, str(shared), "-p", str(free_port()), "-r"],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    assert result.returncode == 1
    assert "Remote access requires an ngrok account" in result.stderr
    assert "Traceback" not in result.stderr
    assert "ERR_NGROK" not in result.stderr
