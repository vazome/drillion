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
_R = ("spec", "rules", 0, "http")  # an Ingress's one rule
_J = ("spec", "jobTemplate", "spec", "template", "spec")  # a CronJob's pod
_JC = ("spec", "template", "spec", "containers", 0)  # a Job's one container
_SP = ("spec", "syncPolicy")  # an Application's sync policy
_TS = ("spec", "template", "spec")  # an ApplicationSet's Application spec
_EL = ("spec", "generators", 0, "list", "elements")
_GIT = ("spec", "generators", 0, "git")
_ST = ("spec", "strategy", "canary", "steps")  # a Rollout's canary steps
_M = ("spec", "metrics", 0)  # an AnalysisTemplate's one metric
_WAVE = "argocd.argoproj.io/sync-wave"
_HOOK = "argocd.argoproj.io/hook"
_DELETE = "argocd.argoproj.io/hook-delete-policy"
_FINALIZER = "resources-finalizer.argocd.argoproj.io"

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
    "306_ingress_host_path": [
        (0, ("kind",), "Service"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "ingressClassName"), DROP),
        (0, ("spec", "rules"), DOUBLE),
        (0, ("spec", "rules", 0, "host"), "zz.example.com"),
        (0, (*_R, "paths"), DOUBLE),
        (0, (*_R, "paths", 0, "path"), "/zz"),
        (0, (*_R, "paths", 0, "pathType"), "Exact"),
        (0, (*_R, "paths", 0, "backend", "service", "name"), WRONG),
        (0, (*_R, "paths", 0, "backend", "service", "port"), {"name": "http"}),
    ],
    "307_ingress_tls": [
        (0, ("kind",), "Service"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "ingressClassName"), WRONG),
        (0, ("spec", "tls"), DROP),
        (0, ("spec", "tls"), DOUBLE),
        (0, ("spec", "tls", 0, "secretName"), WRONG),
        (0, ("spec", "tls", 0, "hosts"), ["www.example.com"]),
        (0, ("spec", "tls", 0, "hosts"), DOUBLE),
        (0, ("spec", "rules", 0, "host"), "www.example.com"),
        (0, (*_R, "paths", 0, "path"), "/zz"),
        (0, (*_R, "paths", 0, "backend", "service", "name"), WRONG),
        (0, (*_R, "paths", 0, "backend", "service", "port", "number"), 443),
    ],
    "308_hpa_cpu": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "replicas"), 3),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_C, "image"), WRONG),
        (0, (*_C, "resources"), DROP),
        (1, ("kind",), "Deployment"),
        (1, ("apiVersion",), "autoscaling/v1"),
        (1, ("spec", "scaleTargetRef", "kind"), "StatefulSet"),
        (1, ("spec", "scaleTargetRef", "name"), WRONG),
        (1, ("spec", "minReplicas"), BIG),
        (1, ("spec", "maxReplicas"), BIG),
        (1, ("spec", "metrics"), DOUBLE),
        (1, ("spec", "metrics", 0, "resource", "name"), "memory"),
        (1, ("spec", "metrics", 0, "resource", "target", "type"), "AverageValue"),
        (1, ("spec", "metrics", 0, "resource", "target", "averageUtilization"), 99),
    ],
    "309_job_batch": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "completions"), BIG),
        (0, ("spec", "backoffLimit"), DROP),
        (0, ("spec", "ttlSecondsAfterFinished"), DROP),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, ("spec", "template", "spec", "containers", 0, "image"), WRONG),
        (0, ("spec", "template", "spec", "containers", 0, "command"), DROP),
        (0, ("spec", "template", "spec", "restartPolicy"), "Always"),
        (0, ("spec", "template", "spec", "restartPolicy"), DROP),
    ],
    "310_cronjob_schedule": [
        (0, ("kind",), "Job"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "schedule"), "* * * * *"),
        (0, ("spec", "schedule"), "0 0 * * 1"),
        (0, ("spec", "schedule"), "61 25 * * *"),
        (0, ("spec", "timeZone"), DROP),
        (0, ("spec", "concurrencyPolicy"), "Allow"),
        (0, ("spec", "concurrencyPolicy"), DROP),
        (0, ("spec", "successfulJobsHistoryLimit"), BIG),
        (0, ("spec", "failedJobsHistoryLimit"), DROP),
        (0, (*_J, "containers"), DOUBLE),
        (0, (*_J, "containers", 0, "image"), WRONG),
        (0, (*_J, "restartPolicy"), "Always"),
    ],
    "311_networkpolicy_default_deny": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "Service"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "podSelector"), {"matchLabels": {"app": "web"}}),
        (0, ("spec", "policyTypes"), ["Ingress", "Egress"]),
        (0, ("spec", "ingress"), [{}]),
        (1, ("metadata", "name"), WRONG),
        (1, ("spec", "podSelector", "matchLabels", "app"), WRONG),
        (1, ("spec", "policyTypes"), DROP),
        (1, ("spec", "ingress"), DOUBLE),
        (1, ("spec", "ingress", 0, "from"), DROP),
        (1, ("spec", "ingress", 0, "from"), DOUBLE),
        (1, ("spec", "ingress", 0, "from", 0, "namespaceSelector"), {}),
        (
            1,
            ("spec", "ingress", 0, "from", 0, "podSelector", "matchLabels", "app"),
            WRONG,
        ),
        (1, ("spec", "ingress", 0, "ports"), DROP),
        (1, ("spec", "ingress", 0, "ports", 0, "port"), BIG),
        (1, ("spec", "ingress", 0, "ports", 0, "protocol"), "UDP"),
    ],
    "312_rbac_least_privilege": [
        (2, (), DROP),
        (2, (), DOUBLE),
        (0, ("kind",), "Role"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), DROP),
        (1, ("kind",), "ClusterRole"),
        (1, ("metadata", "name"), WRONG),
        (1, ("rules",), DOUBLE),
        (1, ("rules", 0, "apiGroups"), ["apps"]),
        (1, ("rules", 0, "resources"), ["secrets"]),
        (1, ("rules", 0, "resources"), DOUBLE),
        (1, ("rules", 0, "verbs"), ["*"]),
        (1, ("rules", 0, "verbs"), ["get", "list", "watch", "delete"]),
        (1, ("rules", 0, "verbs"), ["get"]),
        (2, ("metadata", "namespace"), WRONG),
        (2, ("roleRef", "kind"), "ClusterRole"),
        (2, ("roleRef", "name"), WRONG),
        (2, ("subjects",), DOUBLE),
        (2, ("subjects", 0, "name"), WRONG),
        (2, ("subjects", 0, "namespace"), DROP),
        (2, ("subjects", 0, "kind"), "User"),
    ],
    "313_pod_disruption_budget": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "selector", "matchLabels", "tier"), "web"),
        (0, ("spec", "minAvailable"), BIG),
        (0, ("spec", "minAvailable"), "50%"),
        (0, ("spec", "maxUnavailable"), 1),
    ],
    "357_argocd_first_application": [
        (0, ("kind",), "ApplicationSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "project"), WRONG),
        (0, ("spec", "sources"), [{}]),
        (0, ("spec", "source", "repoURL"), WRONG),
        (0, ("spec", "source", "targetRevision"), WRONG),
        (0, ("spec", "source", "path"), WRONG),
        (0, ("spec", "destination", "name"), "in-cluster"),
        (0, ("spec", "destination", "server"), WRONG),
        (0, ("spec", "destination", "namespace"), WRONG),
        (0, ("spec", "syncPolicy"), {"automated": {}}),
    ],
    "358_argocd_automated_sync": [
        (0, ("kind",), "ApplicationSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "project"), WRONG),
        (0, ("spec", "source", "repoURL"), WRONG),
        (0, ("spec", "source", "targetRevision"), "HEAD"),
        (0, ("spec", "source", "path"), WRONG),
        (0, ("spec", "destination", "server"), WRONG),
        (0, ("spec", "destination", "namespace"), WRONG),
        (0, (*_SP, "automated"), DROP),
        (0, (*_SP, "automated", "prune"), False),
        (0, (*_SP, "automated", "selfHeal"), DROP),
        (0, (*_SP, "syncOptions"), ["CreateNamespace=True"]),
        (0, (*_SP, "syncOptions"), DOUBLE),
        (0, (*_SP, "retry", "limit"), BIG),
        (0, (*_SP, "retry", "backoff", "duration"), "10s"),
        (0, (*_SP, "retry", "backoff", "factor"), 3),
        (0, (*_SP, "retry", "backoff", "maxDuration"), "1h"),
    ],
    "359_argocd_helm_source": [
        (0, ("kind",), "ApplicationSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "project"), WRONG),
        (0, ("spec", "source", "path"), "charts/web"),
        (0, ("spec", "source", "repoURL"), WRONG),
        (0, ("spec", "source", "chart"), WRONG),
        (0, ("spec", "source", "targetRevision"), "main"),
        (0, ("spec", "source", "helm", "releaseName"), WRONG),
        (0, ("spec", "source", "helm", "values"), "replicaCount: 2"),
        (0, ("spec", "source", "helm", "valuesObject"), DROP),
        (0, ("spec", "source", "helm", "valuesObject", "replicaCount"), BIG),
        (0, ("spec", "source", "helm", "valuesObject", "installCRDs"), True),
        (0, ("spec", "destination", "server"), WRONG),
        (0, ("spec", "destination", "namespace"), WRONG),
        (0, (*_SP, "automated", "prune"), False),
        (0, (*_SP, "automated", "selfHeal"), DROP),
        (0, (*_SP, "syncOptions"), ["CreateNamespace=true"]),
    ],
    "360_argocd_sync_waves": [
        (2, (), DROP),
        (2, (), DOUBLE),
        (0, ("kind",), "ConfigMap"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "annotations"), {_WAVE: "-1"}),
        (0, ("spec", "clusterIP"), DROP),
        (0, ("spec", "selector", "app"), WRONG),
        (0, ("spec", "ports", 0, "port"), BIG),
        (0, ("spec", "ports"), DOUBLE),
        (1, ("kind",), "Deployment"),
        (1, ("metadata", "name"), WRONG),
        (1, ("metadata", "annotations"), {_WAVE: "1"}),
        (1, ("spec", "serviceName"), WRONG),
        (1, ("spec", "replicas"), 3),
        (1, ("spec", "selector", "matchLabels", "app"), WRONG),
        (1, ("spec", "template", "metadata", "labels", "app"), WRONG),
        (1, (*_C, "image"), WRONG),
        (1, (*_C, "name"), WRONG),
        (2, ("kind",), "StatefulSet"),
        (2, ("metadata", "name"), WRONG),
        (2, ("metadata", "annotations"), DROP),
        (2, ("metadata", "annotations", _WAVE), "2"),
        (2, ("spec", "replicas"), BIG),
        (2, ("spec", "template", "metadata", "labels", "app"), WRONG),
        (2, ("spec", "template", "spec", "containers"), DOUBLE),
        (2, (*_C, "image"), WRONG),
        (2, (*_C, "env"), DROP),
        (2, (*_C, "env"), DOUBLE),
        (2, (*_C, "env", 0, "value"), WRONG),
    ],
    "361_argocd_presync_migration": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "CronJob"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "annotations", _HOOK), "PostSync"),
        (0, ("metadata", "annotations", _DELETE), "HookSucceeded"),
        (0, ("metadata", "annotations", _DELETE), "BeforeHookCreation"),
        (0, ("metadata", "annotations", _DELETE), "BeforeHookCreation,HookFailed"),
        (0, ("spec", "backoffLimit"), BIG),
        (0, ("spec", "template", "spec", "restartPolicy"), "OnFailure"),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_JC, "name"), WRONG),
        (0, (*_JC, "image"), WRONG),
        (0, (*_JC, "args"), ["migrate"]),
        (0, (*_JC, "env"), DROP),
        (0, (*_JC, "env", 0, "value"), WRONG),
        (1, ("kind",), "StatefulSet"),
        (1, ("metadata", "name"), WRONG),
        (1, ("metadata", "annotations"), {_HOOK: "PreSync"}),
        (1, ("spec", "replicas"), BIG),
        (1, ("spec", "selector", "matchLabels", "app"), WRONG),
        (1, ("spec", "template", "metadata", "labels", "app"), WRONG),
        (1, ("spec", "template", "spec", "containers"), DOUBLE),
        (1, (*_C, "image"), WRONG),
    ],
    "362_argocd_app_of_apps": [
        (2, (), DROP),
        (2, (), DOUBLE),
        (0, ("kind",), "ApplicationSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("metadata", "finalizers"), [_FINALIZER]),
        (0, ("spec", "project"), WRONG),
        (0, ("spec", "source", "repoURL"), WRONG),
        (0, ("spec", "source", "targetRevision"), "HEAD"),
        (0, ("spec", "source", "path"), WRONG),
        (0, ("spec", "destination", "server"), WRONG),
        (0, ("spec", "destination", "namespace"), WRONG),
        (0, (*_SP, "automated", "selfHeal"), False),
        (1, ("metadata", "name"), WRONG),
        (1, ("metadata", "finalizers"), DROP),
        (1, ("metadata", "finalizers"), DOUBLE),
        (1, ("metadata", "annotations", _WAVE), "0"),
        (1, ("spec", "source", "path"), WRONG),
        (1, ("spec", "destination", "namespace"), WRONG),
        (1, (*_SP, "automated"), DROP),
        (1, (*_SP, "syncOptions"), DROP),
        (2, ("metadata", "name"), WRONG),
        (2, ("metadata", "finalizers"), DROP),
        (2, ("metadata", "annotations"), {_WAVE: "-1"}),
        (2, ("spec", "source", "path"), WRONG),
        (2, ("spec", "destination", "namespace"), WRONG),
        (2, (*_SP, "automated", "prune"), False),
        (2, (*_SP, "syncOptions"), DOUBLE),
    ],
    "363_argocd_appproject": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "Application"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "sourceRepos"), ["*"]),
        (0, ("spec", "sourceRepos"), DOUBLE),
        (0, ("spec", "destinations"), DOUBLE),
        (0, ("spec", "destinations", 0, "server"), WRONG),
        (0, ("spec", "destinations", 0, "namespace"), "*"),
        (0, ("spec", "clusterResourceWhitelist"), [{"group": "*", "kind": "*"}]),
        (0, ("spec", "namespaceResourceBlacklist"), DROP),
        (0, ("spec", "namespaceResourceBlacklist"), DOUBLE),
        (0, ("spec", "namespaceResourceBlacklist", 0, "kind"), "NetworkPolicy"),
        (0, ("spec", "namespaceResourceBlacklist", 1, "group"), "apps"),
        (1, ("kind",), "ApplicationSet"),
        (1, ("metadata", "name"), WRONG),
        (1, ("metadata", "namespace"), WRONG),
        (1, ("spec", "project"), "default"),
        (1, ("spec", "source", "repoURL"), WRONG),
        (1, ("spec", "source", "targetRevision"), "HEAD"),
        (1, ("spec", "source", "path"), WRONG),
        (1, ("spec", "destination", "server"), WRONG),
        (1, ("spec", "destination", "namespace"), WRONG),
        (1, (*_SP, "automated", "prune"), False),
        (1, (*_SP, "syncOptions"), ["CreateNamespace=true"]),
    ],
    "364_argocd_ignore_differences": [
        (0, ("kind",), "ApplicationSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "project"), WRONG),
        (0, ("spec", "source", "repoURL"), WRONG),
        (0, ("spec", "source", "path"), WRONG),
        (0, ("spec", "destination", "server"), WRONG),
        (0, ("spec", "destination", "namespace"), WRONG),
        (0, (*_SP, "automated", "selfHeal"), False),
        (0, (*_SP, "syncOptions"), DROP),
        (0, (*_SP, "syncOptions"), ["CreateNamespace=true"]),
        (0, ("spec", "ignoreDifferences"), DROP),
        (0, ("spec", "ignoreDifferences"), DOUBLE),
        (0, ("spec", "ignoreDifferences", 0, "group"), ""),
        (0, ("spec", "ignoreDifferences", 0, "kind"), "StatefulSet"),
        (0, ("spec", "ignoreDifferences", 0, "name"), WRONG),
        (0, ("spec", "ignoreDifferences", 0, "jsonPointers"), ["/spec"]),
        (0, ("spec", "ignoreDifferences", 0, "jsonPointers"), DOUBLE),
        (0, ("spec", "ignoreDifferences", 0, "jqPathExpressions"), [".spec.replicas"]),
    ],
    "365_argocd_appset_list": [
        (0, ("kind",), "Application"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "goTemplate"), False),
        (0, ("spec", "goTemplateOptions"), DROP),
        (0, ("spec", "generators"), DOUBLE),
        (0, ("spec", "generators", 0), {"clusters": {}}),
        (0, _EL, DROP),
        (0, _EL, DOUBLE),
        (0, (*_EL, 0, "url"), WRONG),
        (0, (*_EL, 1, "env"), "qa"),
        (0, ("spec", "template", "metadata", "name"), "checkout"),
        (0, ("spec", "template", "metadata", "name"), "{{.env}}-" + WRONG),
        (0, (*_TS, "project"), WRONG),
        (0, (*_TS, "source", "repoURL"), WRONG),
        (0, (*_TS, "source", "targetRevision"), "HEAD"),
        (0, (*_TS, "source", "path"), WRONG),
        (0, (*_TS, "destination", "server"), "https://kubernetes.default.svc"),
        (0, (*_TS, "destination", "namespace"), WRONG),
        (0, (*_TS, "syncPolicy", "automated", "prune"), False),
        (0, (*_TS, "syncPolicy", "syncOptions"), DROP),
    ],
    "366_argocd_appset_git_directories": [
        (0, ("kind",), "Application"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "namespace"), WRONG),
        (0, ("spec", "goTemplate"), False),
        (0, ("spec", "goTemplateOptions"), ["missingkey=zero"]),
        (0, ("spec", "generators"), DOUBLE),
        (0, (*_GIT, "repoURL"), WRONG),
        (0, (*_GIT, "revision"), "HEAD"),
        (0, (*_GIT, "files"), [{"path": "config.json"}]),
        (0, (*_GIT, "directories"), DOUBLE),
        (0, (*_GIT, "directories", 1), DROP),
        (0, (*_GIT, "directories", 0, "path"), WRONG),
        (0, (*_GIT, "directories", 1, "exclude"), False),
        (0, ("spec", "template", "metadata", "name"), "{{.path.path}}"),
        (0, (*_TS, "project"), WRONG),
        (0, (*_TS, "source", "repoURL"), WRONG),
        (0, (*_TS, "source", "targetRevision"), "HEAD"),
        (0, (*_TS, "source", "path"), "{{.path.basename}}"),
        (0, (*_TS, "destination", "server"), WRONG),
        (0, (*_TS, "destination", "namespace"), WRONG),
        (0, (*_TS, "syncPolicy", "automated", "selfHeal"), False),
        (0, (*_TS, "syncPolicy", "syncOptions"), DROP),
    ],
    "367_argocd_rollout_canary": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "replicas"), BIG),
        (0, ("spec", "selector", "matchLabels", "app"), WRONG),
        (0, ("spec", "template", "metadata", "labels", "app"), WRONG),
        (0, ("spec", "template", "spec", "containers"), DOUBLE),
        (0, (*_C, "name"), WRONG),
        (0, (*_C, "image"), WRONG),
        (0, ("spec", "strategy"), {"blueGreen": {}}),
        (0, _ST, DOUBLE),
        (0, (*_ST, 0, "setWeight"), 150),
        (0, (*_ST, 0), {"setWeight": 20, "pause": {}}),
        (0, (*_ST, 1, "pause", "duration"), "1h"),
        (0, (*_ST, 2, "setWeight"), 100),
        (0, (*_ST, 3, "pause"), {"duration": "1m"}),
    ],
    "368_argocd_canary_analysis": [
        (1, (), DROP),
        (1, (), DOUBLE),
        (0, ("kind",), "ClusterAnalysisTemplate"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "args"), DOUBLE),
        (0, ("spec", "args", 0, "name"), WRONG),
        (0, ("spec", "args", 0, "value"), "checkout"),
        (0, ("spec", "metrics"), DOUBLE),
        (0, (*_M, "name"), WRONG),
        (0, (*_M, "interval"), "5m"),
        (0, (*_M, "count"), DROP),
        (0, (*_M, "failureLimit"), BIG),
        (0, (*_M, "successCondition"), "result[0] >= 0.5"),
        (0, (*_M, "provider"), {"web": {}}),
        (0, (*_M, "provider", "prometheus", "address"), WRONG),
        (0, (*_M, "provider", "prometheus", "query"), WRONG),
        (1, ("kind",), "Deployment"),
        (1, ("metadata", "name"), WRONG),
        (1, ("spec", "replicas"), BIG),
        (1, ("spec", "selector", "matchLabels", "app"), WRONG),
        (1, (*_C, "image"), WRONG),
        (1, _ST, DOUBLE),
        (1, (*_ST, 0, "setWeight"), 30),
        (1, (*_ST, 0), {"setWeight": 20, "pause": {}}),
        (1, (*_ST, 1, "analysis", "templates", 0, "templateName"), WRONG),
        (1, (*_ST, 1, "analysis", "templates"), DOUBLE),
        (1, (*_ST, 1, "analysis", "args"), DROP),
        (1, (*_ST, 1, "analysis", "args", 0, "value"), WRONG),
        (1, (*_ST, 2, "setWeight"), 100),
        (1, (*_ST, 3, "pause", "duration"), "1m"),
    ],
    "369_argocd_diagnose_degraded": [
        (0, ("kind",), "StatefulSet"),
        (0, ("metadata", "name"), WRONG),
        (0, ("spec", "replicas"), 5),
        (0, (*_C, "image"), "ghcr.io/acme/catalog:2.7.3"),
        (0, (*_C, "readinessProbe", "httpGet", "path"), "/health"),
        (0, (*_C, "readinessProbe", "httpGet", "path"), "/healthz"),
        (0, (*_C, "readinessProbe", "periodSeconds"), 1),
        (0, (*_C, "livenessProbe", "periodSeconds"), 5),
        (0, (*_C, "resources"), {}),
        (0, (*_C, "ports"), DROP),
    ],
    "370_argocd_diagnose_failed_sync": [
        (0, ("kind",), "Deployment"),
        (0, ("metadata", "name"), WRONG),
        (0, ("metadata", "annotations", _HOOK), "Sync"),
        (0, ("metadata", "annotations", _DELETE), "HookSucceeded"),
        (0, ("spec", "backoffLimit"), BIG),
        (0, (*_JC, "image"), "ghcr.io/acme/orders:5.0.9"),
        (0, (*_JC, "args"), ["migrate"]),
        (0, (*_JC, "env", 0, "value"), "postgres"),
        (0, (*_JC, "env", 0, "value"), WRONG),
        (0, (*_JC, "env"), DOUBLE),
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
