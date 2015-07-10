# chained-builds-ex

Test app for chained builds on OpenShift v3.

## Usage

### 1. Preparation

In order to speed up builds for this experiment, we're building from a
relatively small Docker image that you have to build yourself (not worth pushing
it to Docker Hub for now).

To build the base image:

    (cd httphostname && make)

### 2. Fun

Create a test project on OpenShift, then run:

    python openshift/templates/gentmpl.py 5 | oc process -f - | oc create -f -

This will create 5 Services, BuildConfigs and DeploymentConfigs.
Starting the first build will trigger the second upon completion, the second
triggers the third and so on.

You can change the chain length by using a different integer in the command line
above.

Start the first build and the chain reaction with:

    oc start-build chained-builds-app1
