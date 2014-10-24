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
Nagios Server:
Copy check_tomcat.py file to a plugins nagios directory, usually in this path:
/usr/local/nagios/libexec

Tomcat Server:
You must define a user for access to the manager webapp, the instructions for define an user:
- [Define user for tomcat6](http://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html#Configuring_Manager_Application_Access)
- [Define user for tomcat7](http://tomcat.apache.org/tomcat-6.0-doc/manager-howto.html#Configuring_Manager_Application_Access)
	Both of them (tomcat6 or tomcat 7) you must define an user with roles "manager-gui" and "manager-script", you must define a line in file tomcat_users.xml like that:
	<user username="nagioscheck" password="my_password" roles="manager-gui,manager-script"/>

Use
===
First, we must test the plugin in the nagios server, in console, we can execute the plugin:
<pre><code>$/path_nagios_libexec/check_tomcat.py</code></pre>

This command show the use of the plugin, with:
<pre><code>$/path_nagios_libexec/check_tomcat.py -h</code></pre>
Show the help

If I have a Tomcat Server with IP 10.20.40.20 and port 8080, for test the plugin, I can execute:
<pre><code>$/path_nagios_libexeccheck_tomcat.py -H 10.20.40.20 -p 8080 -u nagioscheck -a pass -m status</pre></code>
where 10.20.40.20 is the ip of the tomcat server, nagioscheck and pass are the credentials of tomcat manager, command output would be something like:
<pre><code>OK  Apache Tomcat/7.0.53 server is OK</pre></code>

If output is an error, you can execute the command with -v, -vv or -vvv for verbose output, this can help you to find the problem.


	
You must define a command in commands.cfg for nagios, an example:
<pre><code>
define command {
	command_name   check_tomcat
	command_line   $USER1$/check_tomcat.py -H $HOSTADDRESS$ -u $USER10$ -p $ARG1$ -a $USER12$ -U $ARG2$ -m $ARG3$ $ARG4$ $ARG5$ $ARG6$
	register       1
}	
</pre></code>
Now, you can define a service in a service config file (services.cfg for example) for check, for example, the tomcat server memory:
<pre><code>
define service {
	host_name                      	TOMCAT_SERVER
	service_description            	Tomcat Server Memory
	use                            	servicio-generico
	check_command                  	check_tomcat!8080!/manager!mem!-w 80 -c 90
	contact_groups                 	grupo-sistemas
	icon_image                     	../logos2/tomcat.png
	register                       	1
}	
</pre></code>
Note: In the example, a lot of required parameters are defined in the template "servicio-generico" 
