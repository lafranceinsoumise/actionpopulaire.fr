from webpack_loader.loader import WebpackLoader


class DummyWebpackLoader(WebpackLoader):
    def get_bundle(self, bundle_name):
        return [
            {"url": "/dummy.css", "path": "/dummy.css", "name": "dummy.css",},
            {"url": "/dummy.js", "path": "/dummy.js", "name": "dummy.js",},
        ]
