## insdash

#### What is it?

Insdash is an Insurgency Sandstorm gameserver monitoring and management tool build in Python Flask framework.

![DR banner](/dr_banner.png)
![DR widget](/dr_widget.png)


#### How to use this


##### Docker
Probably easyist to use the docker container. By providing your server ip address in the environment variables the mainpage will automaticly show your server stats.
When ommitting this variable mainpage will default to Dutch Recon server stats.

`docker run -d --name insdash -p 5000:5000 -e SERVERIP="YOURSERVERIPHERE" pblaas/insdash`

##### Standalone
Running the app standalone requires you to install a number of Python modules. Eighter install them in a virtual python evironment or in your main system.
The requirements.txt is added to the repo. After all requirements are installed you can run `python app.py`.
If you would like to present your own server stats on the mainpage set the `SERVERIP` variable before you start the app.



#### Affiliation 
I am not affiliated to New World Interactive in any way. Images, Logo's, Icons are the intellectual property of NWI.

#### Screenshots


![DR monitor](/dr_monitor.png)
![DR rcon](/dr_rcon.png)
