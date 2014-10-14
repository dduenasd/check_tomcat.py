check_tomcat.py
===============
Check tomcat server plugin for nagios

Author: Daniel Dueñas Domingo (dduenasd@gmail.com)

Version 2.0

Description
===========
This plugin uses the tomcat manager webapp, this app usually is located in the URL:
http://tomcat-host-name:xxxx/manager
which "tomcat-host-name" is the dns name or ip of the tomcat server and "xxxx" is the port number of the tomcat service (the tomcat port is 8080 by default)
This plugin works in tomcat6 and tomcat7 versions, i don't know if works in previous versions.
This plugin can monitorize this items:
1- tomcat server status
2- tomcat server memory
3- tomcat server thread connectors
4- application status on tomcat server

This plugin uses the nagios plugin python template in
https://github.com/dduenasd/nagios_plugin_template_python

 
Requirements
============
- python 2
	Python must be installed in nagios server.
	I use python 2.7, python 3 is not tested for this plugin.
- Tomcat Manager Webapp
	The tomcat server for monitorize must be installed the manager web app
	The documentation of the manager of tomcat:
	- Tomcat 6 -> [Manager_Howto_Tomcat6](http://tomcat.apache.org/tomcat-6.0-doc/manager-howto.html)
	- Tomcat 7 -> [Manager_Howto_Tomcat7](http://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html)


Installation
============
Copy check_tomcat.py file to a plugins nagios directory, usually in this path:
/usr/local/nagios/libexec


Use
===
