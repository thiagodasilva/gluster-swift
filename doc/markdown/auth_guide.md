# Authentication Services Start Guide

## Contents
* [GSwauth](#gswauth)

<a name="gswauth" />
GSwauth
------

An easily deployable GlusterFS aware authentication service based on Swauth.
GSwauth is a WSGI Middleware that uses Swift itself as a backing store to 
maintain its metadata.

This model has the benefit of having the metadata available to all proxy servers
and saving the data to a GlusterFS volume. To protect the metadata, the GlusterFS
volume should only be able to be mounted by the systems running the proxy servers.

Currently, gluster-swift has a strict mapping of an account to a GlusterFS volume. 
Future releases, this will be enhanced to support multiple accounts per GlusterFS
volume.

See <http://gholt.github.com/swauth/> for more information on Swauth.

See also <https://github.com/openstack/keystone> for the standard OpenStack
authentication service.


Quick Install
-------------

1. GSwauth is installed by default with Gluster for Swift.

2. After installation, alter your proxy-server.conf pipeline to have gswauth instead of tempauth:

Was:

    [pipeline:main]
    pipeline = catch_errors cache tempauth proxy-server

Change To:

    [pipeline:main]
    pipeline = catch_errors cache gswauth proxy-server

3. Add to your proxy-server.conf the section for the Swauth WSGI filter:

    [filter:swauth]
    use = egg:gluster_swift#gswauth
    set log_name = swauth
    super_admin_key = swauthkey

4. Be sure your proxy server allows account management:

    [app:proxy-server]
    ...
    allow_account_management = true

5. Restart your proxy server ``swift-init proxy reload``

6. Initialize the GSwauth backing store in Gluster-Swift ``swauth-prep -K swauthkey``

7. Add an account/user ``swauth-add-user -A http://127.0.0.1:8080/auth/ -K
   swauthkey -a volumename user1 password1``

8. Ensure it works ``swift -A http://127.0.0.1:8080/auth/v1.0 -U volumename:user1 -K
   password stat -v``
