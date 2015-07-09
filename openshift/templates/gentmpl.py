def objects(app):
    service = {
        "kind": "Service",
        "apiVersion": "v1",
        "metadata": {
            "name": "python-{}-frontend".format(app),
            "annotations": {
                "description": "Exposes and load balances the application pods"
            }
        },
        "spec": {
            "ports": [
                {
                    "name": "web",
                    "port": 8080,
                    "targetPort": 8080
                }
            ],
            "selector": {
                "name": "python-{}-frontend".format(app)
            }
        }
    }

    imagestream = {
        "kind": "ImageStream",
        "apiVersion": "v1",
        "metadata": {
            "name": "python-static-{}".format(app),
            "annotations": {
                "description": "Keeps track of changes in the application image"
            }
        }
    }

    buildconfig = {
        "kind": "BuildConfig",
        "apiVersion": "v1",
        "metadata": {
            "name": "python-static-{}".format(app),
            "annotations": {
                "description": "Defines how to build the application"
            }
        },
        "spec": {
            "source": {
                "type": "Git",
                "git": {
                    "uri": "${SOURCE_REPOSITORY_URL}",
                    "ref": "${SOURCE_REPOSITORY_REF}"
                },
                "contextDir": app
            },
            "strategy": {
                "type": "Source",
                "sourceStrategy": {
                    "from": {
                        "kind": "ImageStreamTag",
                        "namespace": "openshift",
                        "name": "python:3.3"
                    }
                }
            },
            "output": {
                "to": {
                    "kind": "ImageStreamTag",
                    "name": "python-static-{}:latest".format(app)
                }
            },
            "triggers": [
                {
                    "type": "ImageChange"
                },
                {
                    "type": "GitHub",
                    "github": {
                        "secret": "${GITHUB_WEBHOOK_SECRET}"
                    }
                },
                {
                    "type": "Generic",
                    "github": {
                        "secret": "${GENERIC_WEBHOOK_SECRET}"
                    }
                }
            ]
        }
    }

    deploymentconfig = {
        "kind": "DeploymentConfig",
        "apiVersion": "v1",
        "metadata": {
            "name": "python-frontend",
            "annotations": {
                "description": "Defines how to deploy the application server"
            }
        },
        "spec": {
            "strategy": {
                "type": "Rolling"
            },
            "triggers": [
                {
                    "type": "ImageChange",
                    "imageChangeParams": {
                        "automatic": True,
                        "containerNames": [
                            "python-static"
                        ],
                        "from": {
                            "kind": "ImageStreamTag",
                            "name": "python-static-{}:latest".format(app)
                        }
                    }
                },
                {
                    "type": "ConfigChange"
                }
            ],
            "replicas": 1,
            "selector": {
                "name": "python-frontend"
            },
            "template": {
                "metadata": {
                    "name": "python-frontend",
                    "labels": {
                        "name": "python-frontend"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": "python-static",
                            "image": "python-static-{}".format(app),
                            "ports": [
                                {
                                    "containerPort": 8080
                                }
                            ],
                        }
                    ]
                }
            }
        }
    }

    return [service, imagestream, buildconfig, deploymentconfig]


if __name__ == "__main__":
    import json
    import os.path
    with open(os.path.join(os.path.dirname(__file__), "python-static.json")) as f:
        tmpl = json.load(f)
        objs = objects("app1")
        # objs[-1]["spec"]["strategy"]["rollingParams"] = {
        #     "pre": {
        #         "failurePolicy": "Abort",
        #         "execNewPod": {
        #             "containerName": "python-static",
        #             "command": [
        #                 "curl", "http://<openshift_api_host:port>/osapi/v1/namespaces/<namespace>/buildconfigs/<name>/webhooks/<secret>/generic"
        #             ],
        #             "env": [
        #                 {
        #                 "name": "CUSTOM_VAR1",
        #                 "value": "custom_value1"
        #                 }
        #             ]
        #         }
        #     }
        # }
        tmpl["objects"].extend(objs)
        tmpl["objects"].extend(objects("app2"))
        print(json.dumps(tmpl))
