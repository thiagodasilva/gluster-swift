# Authentication Services Start Guide

## Contents
* [Keystone](#keystone)
* [Swiftkerbauth](#swiftkerbauth)
* [GSwauth](#gswauth)
 * [Overview](#gswauth_overview)
 * [Quick Install](#gswauth_quick_install)
 * [How to use it](#swauth_use)

<a name="keystone" />
## Keystone
The Standard Openstack authentication service

TBD

<a name="swiftkerbauth" />
## Swiftkerbauth
Kerberos authentication filter for Swift

TBD

<a name="gswauth" />
## GSwauth

<a name="gswauth_overview" />
## Overview
An easily deployable GlusterFS aware authentication service based on [Swauth](http://gholt.github.com/swauth/).
GSwauth is a WSGI Middleware that uses Swift itself as a backing store to 
maintain its metadata.

This model has the benefit of having the metadata available to all proxy servers
and saving the data to a GlusterFS volume. To protect the metadata, the GlusterFS
volume should only be able to be mounted by the systems running the proxy servers.

Currently, gluster-swift has a strict mapping of one account to a GlusterFS volume. 
Future releases, this will be enhanced to support multiple accounts per GlusterFS
volume.

See <http://gholt.github.com/swauth/> for more information on Swauth.

<a name="gswauth_quick_install" />
##Quick Install

1. GSwauth is installed by default with Gluster for Swift.

2. Create and start the `gsmetadata` gluster volume and run `gluster-swift-gen-bduilders` with all 
   volumes that should be accessable by gluster-swift, including `gsmetadata`

3. Change your proxy-server.conf pipeline to have gswauth instead of tempauth:

    Was:
    ```
    [pipeline:main]
    pipeline = catch_errors cache tempauth proxy-server
    ```
    Change To:
    ```
    [pipeline:main]
    pipeline = catch_errors cache gswauth proxy-server
    ```

4. Add to your proxy-server.conf the section for the Swauth WSGI filter:
```
    [filter:gswauth]

    use = egg:gluster_swift#gswauth
    set log_name = gswauth
    super_admin_key = swauthkey
```
5. Be sure your proxy server allows account management:
```
    [app:proxy-server]
    ...
    allow_account_management = true
```
6. Restart your proxy server ``swift-init proxy reload``

<a name="swauth_use" />
##How to use it
1. Initialize the GSwauth backing store in Gluster-Swift ``swauth-prep -K swauthkey``

1. Add an account/user ``swauth-add-user -A http://127.0.0.1:8080/auth/ -K
   swauthkey -a volumename user1 password1``
   
1. Ensure it works ``swift -A http://127.0.0.1:8080/auth/v1.0 -U volumename:user1 -K
   password stat -v``
