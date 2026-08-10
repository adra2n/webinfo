import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocs.base import POCBase, POCResult
from pocs.docker_unauth import DockerUnauth
from pocs.redis_unauth import RedisUnauth
from pocs.etcd_unauth import EtcdUnauth
from pocs.supervisor_unauth import SupervisorUnauth


class TestPOCBase(unittest.TestCase):
    def test_poc_base_not_implemented(self):
        poc = POCBase()
        with self.assertRaises(NotImplementedError):
            poc.check("127.0.0.1", 80)

    def test_build_url_http(self):
        poc = POCBase()
        url = poc.build_url("1.2.3.4", 80)
        self.assertEqual(url, "http://1.2.3.4:80")

    def test_build_url_https(self):
        poc = POCBase()
        url = poc.build_url("1.2.3.4", 443)
        self.assertEqual(url, "https://1.2.3.4:443")

    def test_build_url_8443(self):
        poc = POCBase()
        url = poc.build_url("1.2.3.4", 8443)
        self.assertEqual(url, "https://1.2.3.4:8443")


class TestPOCNames(unittest.TestCase):
    def test_docker_unauth(self):
        self.assertEqual(DockerUnauth().name, "docker_unauth")

    def test_redis_unauth(self):
        self.assertEqual(RedisUnauth().name, "redis_unauth")

    def test_etcd_unauth(self):
        self.assertEqual(EtcdUnauth().name, "etcd_unauth")

    def test_supervisor_unauth(self):
        self.assertEqual(SupervisorUnauth().name, "supervisor_unauth")


if __name__ == "__main__":
    unittest.main()
