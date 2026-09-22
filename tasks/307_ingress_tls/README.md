---
title: HTTPS at the Ingress, with the certificate in a Secret
difficulty: medium
minutes: 15
prereqs: [306, 271]
track: kubernetes
tags: [ingress, networking, secret]
kind: manifest
---
# HTTPS at the Ingress, with the certificate in a Secret

*The app behind an Ingress can speak plain HTTP. The certificate lives in one place, the edge, and the Ingress says which Secret holds it and which host names it covers.*

## Read first
- [Ingress: TLS](https://kubernetes.io/docs/concepts/services-networking/ingress/#tls): the `tls` block and the Secret it names
- [TLS Secrets](https://kubernetes.io/docs/concepts/configuration/secret/#tls-secrets): the `kubernetes.io/tls` type and its two keys

## Why
Every public site needs HTTPS, and nobody wants a certificate baked into twenty app images, each renewed separately. The usual shape is to end TLS at the Ingress: the controller holds the certificate, decrypts the request, and forwards it to the Service over the cluster network.

The certificate and its private key go in a Secret of type `kubernetes.io/tls`, under the keys `tls.crt` and `tls.key`, in the same namespace as the Ingress. In most clusters nobody writes that Secret by hand: cert-manager watches Ingress objects, gets a certificate from Let's Encrypt, and writes the Secret under the name the Ingress asked for. Either way, the Ingress's side is the same.

That side is the `tls` list. Each entry names a Secret and the hosts its certificate covers. The hosts have to be the same names the rules route. A rule for `shop.example.com` with a `tls` entry for `www.shop.example.com` serves HTTPS with a certificate for the wrong name, and every browser refuses it.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Ingress named `{name}`, for the `{ingressClass}` controller, that serves `{host}` over HTTPS with the certificate in the Secret `{secret}`, and sends all of its traffic to the Service `{service}` on port 80.

## Rules
- one Ingress, `apiVersion: networking.k8s.io/v1`, with `ingressClassName: {ingressClass}`
- exactly one `tls` entry, with `secretName: {secret}` and `hosts` holding `{host}` and nothing else
- exactly one rule, for the host `{host}`, with one path: `/`, `pathType: Prefix`, to the Service `{service}` on port number 80
- the host in `tls` and the host in the rule are the same string

## Hints
### Hint 1
`tls` sits on the Ingress's `spec`, beside `rules`, and is a list:

```yaml
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - shop.example.com
      secretName: shop-tls
  rules:
    - ...
```

### Hint 2
The rule is the same shape as in 306. Nothing in it changes for HTTPS: the controller matches the host, finds the `tls` entry for it, and uses that certificate.

### Hint 3
If you ever write the Secret yourself, its shape is fixed by its type:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: shop-tls
type: kubernetes.io/tls
data:
  tls.crt: <base64 of the certificate>
  tls.key: <base64 of the private key>
```

The task asks only for the Ingress. The Secret is assumed to exist, as it does when cert-manager writes it.
