"""Quick and dirty OpenShift template generator for chained builds."""


def create_chained_builds(base_template, chain_length):
    for i in xrange(1, chain_length+1):
        objs = generate_app_objects("app{}".format(i))
        if i < chain_length:
            add_deployment_hook(objs[-1], i)
        tmpl["objects"].extend(objs)


def add_deployment_hook(deploymentconfig, i):
    deploymentconfig["spec"]["strategy"]["rollingParams"] = {
        "pre": {
            "failurePolicy": "Abort",
            "execNewPod": {
                "containerName": "chained-builds",
                "command": [
                    "sh", "-c", """
WEBHOOK_URL="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT/osapi/v1beta3/namespaces/$TARGET_BUILDCONFIG_NAMESPACE/buildconfigs/$TARGET_BUILDCONFIG_NAME/webhooks/$GENERIC_WEBHOOK_SECRET/generic";
test `curl -skXPOST -w %{http_code} $WEBHOOK_URL` = 200 || >&2 echo -e "FAILURE: call to generic webhook trigger for BuildConfig $TARGET_BUILDCONFIG_NAMESPACE/$TARGET_BUILDCONFIG_NAME failed.\nWebhook URL: $WEBHOOK_URL"
"""
                ],
                "env": [
                    {
                        "name": "TARGET_BUILDCONFIG_NAMESPACE",
                        "value": "demo"
                    },
                    {
                        "name": "TARGET_BUILDCONFIG_NAME",
                        "value": "chained-builds-app{}".format(i+1)
                    },
                    {
                        "name": "GENERIC_WEBHOOK_SECRET",
                        "value": "${GENERIC_WEBHOOK_SECRET}"
                    }
                ]
            }
        }
    }


def generate_app_objects(app):
    service = {
        "kind": "Service",
        "apiVersion": "v1",
        "metadata": {
            "name": "chain-{}-frontend".format(app),
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
                "name": "chain-{}-frontend".format(app)
            }
        }
    }
    imagestream = {
        "kind": "ImageStream",
        "apiVersion": "v1",
        "metadata": {
            "name": "chained-builds-{}".format(app),
            "annotations": {
                "description": "Keeps track of changes in the application image"
            }
        }
    }
    buildconfig = {
        "kind": "BuildConfig",
        "apiVersion": "v1",
        "metadata": {
            "name": "chained-builds-{}".format(app),
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
                "contextDir": "app"
            },
            "strategy": {
                "type": "Docker"
            },
            "output": {
                "to": {
                    "kind": "ImageStreamTag",
                    "name": "chained-builds-{}:latest".format(app)
                }
            },
            "triggers": [
                {
                    "type": "ImageChange"
                },
                {
                    "type": "Generic",
                    "generic": {
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
            "name": "chain-{}-frontend".format(app),
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
                            "chained-builds"
                        ],
                        "from": {
                            "kind": "ImageStreamTag",
                            "name": "chained-builds-{}:latest".format(app)
                        }
                    }
                },
                {
                    "type": "ConfigChange"
                }
            ],
            "replicas": 1,
            "selector": {
                "name": "chain-{}-frontend".format(app)
            },
            "template": {
                "metadata": {
                    "name": "chain-{}-frontend".format(app),
                    "labels": {
                        "name": "chain-{}-frontend".format(app)
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": "chained-builds",
                            "image": "chained-builds-{}".format(app),
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
    import sys
    try:
        chain_length = int(sys.argv[1])
    except (ValueError, IndexError):
        chain_length = 2
    with open(os.path.join(os.path.dirname(__file__), "chained-builds.json")) as f:
        tmpl = json.load(f)
        create_chained_builds(tmpl, chain_length)
        print(json.dumps(tmpl))
