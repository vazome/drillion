"""Every rule a manifest task shows the learner is one its grader enforces.

The answer key passes, and each mutation below breaks exactly one displayed rule and must
fail. A rule with no row here is a rule a wrong manifest can pass."""

import copy
import importlib.util
import random

import pytest
import yaml

from drillion import catalogue, manifest

DROP, DOUBLE = object(), object()
WRONG, BIG = "zz-wrong", 99999
_C = ("spec", "template", "spec", "containers", 0)  # a Deployment's one container
_SC = ("spec", "containers", 0, "securityContext")  # a Pod's one container's

# (document, path, what to put there). DROP deletes the key, DOUBLE appends a copy of the
# list's first item. A path of () with DROP/DOUBLE removes or repeats a whole document.
BREAKS = {
    "268_first_deployment": [
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "replicas"), BIG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "metadata", "labels"), DROP),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, ("spec", "template", "spec", "containers", 0, "image"), WRONG),
    ],
    "269_bare_pod": [
        (0, ("kind",), "Service"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "containers"), DOUBLE),
        (0, ("spec", "containers", 0, "image"), WRONG),
        (0, ("spec", "containers", 0, "ports"), DROP),
        (0, ("spec", "containers", 0, "ports", 0, "containerPort"), BIG),
    ],
    "270_configmap_env": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "Secret"),
        (0, ("metadata", "name"), WRONG),
        (0, ("data", "LOG_LEVEL"), WRONG),
        (1, ("kind",), "Service"),
        (1, ("spec", "containers"), DOUBLE),
        (1, ("spec", "containers", 0, "image"), DROP),
        (1, ("spec", "containers", 0, "env", 0, "name"), WRONG),
        (1, ("spec", "containers", 0, "env", 0, "value"), "debug"),
        (
            1,
            ("spec", "containers", 0, "env", 0, "valueFrom", "configMapKeyRef", "name"),
            WRONG,
        ),
        (
            1,
            ("spec", "containers", 0, "env", 0, "valueFrom", "configMapKeyRef", "key"),
            WRONG,
        ),
    ],
    "271_secret_stringdata": [
        (0, ("kind",), "ConfigMap"),
        (0, ("metadata", "name"), WRONG),
        (0, ("type",), "kubernetes.io/tls"),
        (0, ("data",), {"API_KEY": "c2VjcmV0"}),
        (0, ("stringData", "API_KEY"), WRONG),
    ],
    "272_service_clusterip": [
        (0, ("kind",), "Pod"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "type"), "NodePort"),
        (0, ("spec", "selector", "app"), WRONG),
        (0, ("spec", "ports"), DOUBLE),
        (0, ("spec", "ports", 0, "port"), BIG),
        (0, ("spec", "ports", 0, "targetPort"), BIG),
    ],
    **{
        slug: [
            (0, ("kind",), "Pod"),
            (0, ("metadata", "name"), WRONG),
            (0, ("spec", "type"), "ClusterIP"),
            (0, ("spec", "selector", "app"), WRONG),
            (0, ("spec", "ports"), DOUBLE),
            (0, ("spec", "ports", 0, "port"), BIG),
            (0, ("spec", "ports", 0, "targetPort"), BIG),
            (0, ("spec", "ports", 0, "nodePort"), DROP),
            (0, ("spec", "ports", 0, "nodePort"), BIG),
            (0, ("spec", "ports", 0, "nodePort"), 8080),
        ]
        for slug in ("273_service_nodeport", "274_service_loadbalancer")
    },
    "275_statefulset_headless": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "Pod"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "clusterIP"), DROP),
        (0, ("spec", "selector", "app"), WRONG),
        (0, ("spec", "ports", 0, "port"), BIG),
        (1, ("kind",), "Deployment"),
        (1, ("metadata", "name"), WRONG),
        (1, ("spec", "serviceName"), WRONG),
        (1, ("spec", "replicas"), BIG),
        (1, ("spec", "selector", "matchLabels", "app"), WRONG),
        (1, ("spec", "template", "spec", "containers"), DOUBLE),
        (1, ("spec", "template", "spec", "containers", 0, "image"), WRONG),
    ],
    "276_daemonset": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "replicas"), 3),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, ("spec", "template", "spec", "containers", 0, "name"), WRONG),
        (0, ("spec", "template", "spec", "containers", 0, "image"), WRONG),
    ],
    "277_pv_pvc": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "PersistentVolumeClaim"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "capacity", "storage"), "1G"),
        (0, ("spec", "accessModes"), DOUBLE),
        (0, ("spec", "storageClassName"), WRONG),
        (0, ("spec", "hostPath", "path"), "/tmp"),
        (0, ("spec", "hostPath"), DROP),
        (1, ("kind",), "PersistentVolume"),
        (1, ("spec", "resources", "requests", "storage"), "9Gi"),
        (1, ("spec", "accessModes"), ["ReadOnlyMany"]),
        (1, ("spec", "storageClassName"), WRONG),
    ],
    "278_storageclass_policy": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "PersistentVolume"),
        (0, ("metadata", "name"), WRONG),
        (0, ("provisioner",), WRONG),
        (0, ("reclaimPolicy",), "Recycle"),
        (0, ("volumeBindingMode",), "Immediate"),
        (1, ("kind",), "PersistentVolume"),
        (1, ("metadata", "name"), WRONG),
        (1, ("spec", "storageClassName"), WRONG),
        (1, ("spec", "accessModes"), ["ReadWriteMany"]),
        (1, ("spec", "resources", "requests", "storage"), "9Gi"),
    ],
    "299_probes_readiness_liveness": [
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_C, "image"), WRONG),
        (0, (*_C, "ports", 0, "containerPort"), BIG),
        (0, (*_C, "readinessProbe"), DROP),
        (0, (*_C, "readinessProbe", "httpGet", "path"), "/healthz"),
        (0, (*_C, "readinessProbe", "httpGet", "port"), BIG),
        (0, (*_C, "readinessProbe"), {"tcpSocket": {"port": "http"}}),
        (0, (*_C, "livenessProbe"), DROP),
        (0, (*_C, "livenessProbe", "httpGet", "path"), "/ready"),
        (0, (*_C, "livenessProbe", "httpGet", "port"), "metrics"),
    ],
    "300_startup_probe": [
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_C, "image"), WRONG),
        (0, (*_C, "startupProbe"), DROP),
        (0, (*_C, "startupProbe", "httpGet", "path"), "/ready"),
        (0, (*_C, "startupProbe", "httpGet", "port"), BIG),
        (0, (*_C, "startupProbe", "failureThreshold"), 3),
        (0, (*_C, "startupProbe", "failureThreshold"), DROP),
        (0, (*_C, "startupProbe", "periodSeconds"), 1),
        (0, (*_C, "livenessProbe"), DROP),
        (0, (*_C, "livenessProbe", "httpGet", "path"), "/ready"),
        (0, (*_C, "livenessProbe", "initialDelaySeconds"), 300),
    ],
    "301_requests_limits_qos": [
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_C, "image"), WRONG),
        (0, (*_C, "resources", "requests"), DROP),
        (0, (*_C, "resources", "requests", "cpu"), "3"),
        (0, (*_C, "resources", "requests", "memory"), "3Gi"),
        (0, (*_C, "resources", "limits", "cpu"), "3"),
        (0, (*_C, "resources", "limits", "memory"), "3Gi"),
        (0, (*_C, "resources", "limits", "memory"), DROP),
    ],
    "302_hardened_pod": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "containers"), DOUBLE),
        (0, ("spec", "containers", 0, "image"), WRONG),
        (0, ("spec", "securityContext", "runAsNonRoot"), DROP),
        (0, ("spec", "securityContext", "runAsNonRoot"), False),
        (0, ("spec", "securityContext", "runAsUser"), 0),
        (0, ("spec", "securityContext", "seccompProfile", "type"), "Unconfined"),
        (0, (*_SC, "allowPrivilegeEscalation"), True),
        (0, (*_SC, "readOnlyRootFilesystem"), DROP),
        (0, (*_SC, "capabilities", "drop"), ["NET_RAW"]),
        (0, ("spec", "containers", 0, "volumeMounts"), DROP),
        (0, ("spec", "volumes", 0), {"name": "tmp", "hostPath": {"path": "/tmp"}}),
    ],
    "303_rollout_strategy": [
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "replicas"), BIG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_C, "image"), WRONG),
        (0, ("spec", "strategy"), {"type": "Recreate"}),
        (0, ("spec", "strategy", "rollingUpdate", "maxUnavailable"), 1),
        (0, ("spec", "strategy", "rollingUpdate", "maxUnavailable"), DROP),
        (0, ("spec", "strategy", "rollingUpdate", "maxSurge"), 5),
        (0, ("spec", "minReadySeconds"), DROP),
        (0, (*_C, "readinessProbe"), DROP),
    ],
    "304_init_container": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "initContainers"), DROP),
        (0, ("spec", "initContainers"), DOUBLE),
        (0, ("spec", "containers"), DOUBLE),
        (0, ("spec", "initContainers", 0, "image"), WRONG),
        (0, ("spec", "containers", 0, "image"), WRONG),
        (0, ("spec", "initContainers", 0, "command"), DROP),
        (0, ("spec", "initContainers", 0, "command"), ["sh", "-c", "echo hi > /x"]),
        (0, ("spec", "initContainers", 0, "volumeMounts"), DROP),
        (0, ("spec", "containers", 0, "volumeMounts", 0, "mountPath"), "/wrong"),
        (0, ("spec", "volumes", 0), {"name": "content", "hostPath": {"path": "/x"}}),
    ],
    "305_configmap_volume": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "Secret"),
        (0, ("metadata", "name"), WRONG),
        (0, ("data",), {"other.conf": "x"}),
        (1, ("kind",), "Deployment"),
        (1, ("metadata", "name"), WRONG),
        (1, ("spec", "containers"), DOUBLE),
        (1, ("spec", "containers", 0, "image"), WRONG),
        (1, ("spec", "volumes", 0, "configMap", "name"), WRONG),
        (1, ("spec", "containers", 0, "volumeMounts"), DROP),
        (1, ("spec", "containers", 0, "volumeMounts", 0, "mountPath"), "/wrong"),
        (1, ("spec", "containers", 0, "volumeMounts", 0, "subPath"), "app.conf"),
    ],
}
SEEDS = range(8)


def _grader(meta):
    spec = importlib.util.spec_from_file_location(
        manifest.module_name(meta["dir"].name), meta["dir"] / "grade.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _judge(grade, docs, brief):
    if hasattr(grade, "check_many"):
        grade.check_many(docs, brief)
    else:
        assert len(docs) == 1
        grade.check(docs[0], brief)


def _broken(docs, doc, path, value):
    docs = copy.deepcopy(docs)
    if not path:
        if value is DROP:
            del docs[doc]
        else:
            docs.append(copy.deepcopy(docs[doc]))
        return docs
    *parents, last = path
    node = docs[doc]
    for step in parents:
        node = node[step]
    if value is DROP:
        del node[last]
    elif value is DOUBLE:
        node[last].append(copy.deepcopy(node[last][0]))
    else:
        node[last] = value
    return docs


def _manifests():
    return {
        slug: meta
        for slug, meta in catalogue.tasks().items()
        if meta.get("kind") == catalogue.MANIFEST
    }


def test_every_manifest_task_has_its_rules_listed():
    assert set(_manifests()) == set(BREAKS)


@pytest.mark.parametrize("slug", sorted(BREAKS))
def test_the_answer_key_passes_and_every_broken_rule_fails(slug):
    meta = _manifests()[slug]
    grade = _grader(meta)
    for seed in SEEDS:
        brief = grade.brief(random.Random(seed))
        docs = list(yaml.safe_load_all(manifest.render_solution(meta, brief)))
        _judge(grade, docs, brief)
        for doc, path, value in BREAKS[slug]:
            with pytest.raises(AssertionError):
                _judge(grade, _broken(docs, doc, path, value), brief)


@pytest.mark.parametrize("slug", ["275_statefulset_headless", "276_daemonset"])
def test_a_controller_relabelled_on_both_sides_still_fails(slug):
    """Selector and template agreeing with each other is not enough: the rule names the
    label, and in 275 the Service selects the pods by it."""
    meta = _manifests()[slug]
    grade = _grader(meta)
    brief = grade.brief(random.Random(SEEDS[0]))
    docs = list(yaml.safe_load_all(manifest.render_solution(meta, brief)))
    spec = docs[-1]["spec"]
    spec["selector"]["matchLabels"]["app"] = WRONG
    spec["template"]["metadata"]["labels"]["app"] = WRONG
    with pytest.raises(AssertionError):
        _judge(grade, docs, brief)
