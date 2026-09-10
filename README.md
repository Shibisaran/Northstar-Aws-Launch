# **Low-Cost, Highly Available and Scalable Cloud Infrastructure for Startups**

### **1\. Project Overview**

Startups and small companies often face a major challenge when moving their applications to the cloud. They need their applications to be **available, secure and capable of handling increasing traffic**, but they cannot afford the same infrastructure and operational complexity used by large enterprises.

A traditional cloud deployment may involve multiple servers, databases, networking components, monitoring systems, security services and backup solutions. If these services are configured without considering cost, the monthly cloud bill can quickly become difficult for a startup to manage.

The objective of this project is therefore to design and deploy a **cost-conscious three-tier AWS architecture** that provides:

* **Low infrastructure cost**  
* **High availability**  
* **Scalability**  
* **Security**  
* **Performance**  
* **Monitoring and alerting**  
* **Disaster recovery capability**  
* **Easy troubleshooting and maintenance**

## **Real-World Problem Statement**

Consider a startup that has developed a web application but has limited financial resources.

Initially, the company may have only a small number of users. A single EC2 instance might appear sufficient.

### **Problem 1 — High cloud cost**

Using large instances and expensive managed services from the beginning can create unnecessary costs for a startup.

### **Problem 2 — Increasing traffic**

When the number of users increases, one server may not have enough CPU, memory or network capacity to handle all requests.

### **Problem 3 — Database security**

The application database should not be directly accessible from the public internet.

### **Problem 4 — No automatic notification**

Even when monitoring exists, administrators may not notice an alarm immediately.

### **Problem 5 — Operational failures**

Incorrect security groups, routing, IAM permissions, database configuration or load-balancer health checks can cause application outages.

The proposed architecture addresses these problems while attempting to keep the infrastructure appropriate for a startup rather than building an unnecessarily expensive enterprise environment.

## **Architecture Diagram**

## **![image alt](https://github.com/Shibisaran/Northstar-Aws-Launch/blob/03c20777f6bfabe97bfcddcab4e16fc7261b5752/screenshots/Architecture.jpg)**

## **Tier 1 — Presentation Layer**

The presentation layer is responsible for receiving requests from users.  
Components include:

* DNS  
* Cloudflare  
* CloudFront  
* Application Load Balancer  
* Public-facing infrastructure

The **Application Load Balancer** distributes incoming requests between multiple EC2 instances rather than allowing all traffic to depend on a single server.

## **Tier 2 — Application Layer**

The application layer contains the actual web application. In the current project, this can be the **Flask application running on EC2**. Running multiple application instances provides redundancy.

## **Tier 3 — Database Layer**

The database layer uses **Amazon RDS**. The database is placed inside private subnets rather than exposing it directly to the internet. For the startup scenario, this provides a managed database without requiring the company to manually maintain a database server.

# **Cost Optimization Strategy**

The primary objective is “**Not simply use AWS cheaply instead Efficiently under cost."**

| Requirement | Cost-conscious approach |
| ----- | ----- |
| Web application | Small EC2 instances initially |
| High availability | Minimum two application instances |
| Traffic distribution | ALB |
| Static files | S3 \+ CloudFront |
| Database | Right-sized RDS |
| Storage | Right-sized EBS |
| Monitoring | CloudWatch |
| Alerts | SNS |
| Access | IAM roles instead of access keys |
| Scaling | Auto Scaling as traffic grows |
| Backups | Automated database backups |
| DNS/security | Cloudflare where appropriate |

## **Major Problems Faced During Implementation**

### **Troubleshoot ELB Issues**

An Application Load Balancer is unable to serve the application.  
Identify and resolve all configuration issues preventing successful access.

Problems faced

1)  SSH connection isn't connected to the server with the security group only with my ip address   
2) Can’t write or execute index.html file without changing the permissions  
3) Webpage is not loading even after   
   “Sudo yum install https \-y”  
   “Sudo systemctl start httpd”  
   	“Sudo systemctl enable httpd”  
4) Even if i allow https in the launch template i can’t open the file   
5) Now I can open with the file but I need to change the https:// to http://, but why?

Target Group Health : healthy  
Are both EC2 instances running: yes (tried both http only or https only or both in inbound and outbound rules)  
Apache running : Active  
ALB Listener : http → target group

![][image2]

Troubleshoots measures

1) Security group to allow all traffic in inbound and outbound network traffic(which is not safe for production- probably use required protocols)  
2) Check availability zones are same in both load balancer and instances

### **Flask/Gunicorn Problem**

For the Flask application, one major operational problem can occur when the application works during testing but stops after the terminal session closes.

### **Example**

python app.py

works while connected through SSH.

After disconnecting:

Application → unavailable

### **Root cause**

The Flask development process was tied to the terminal session.

### **Solution**

Use a production application server such as Gunicorn and configure it as a system service.

This makes the application behave like a persistent production service instead of a manually executed development process.

![][image3]

install Gunicorn inside your virtual environment:

cd /home/ec2-user/Northstar-Aws-Launch  
source .venv/bin/activate  
pip install gunicorn

Then verify: which gunicorn

It should show something similar to:

/home/ec2-user/Northstar-Aws-Launch/.venv/bin/gunicorn

**Test Gunicorn manually**

Before touching Nginx, test the application:

cd /home/ec2-user/Northstar-Aws-Launch  
source .venv/bin/activate  
gunicorn \--bind 127.0.0.1:8000 app:app

If your Flask file is app.py and contains:

app \= Flask(\_\_name\_\_)

then app:app is correct.

If it starts successfully, you should see something like:

Listening at: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
**Check your systemd service**

Run:

sudo cat /etc/systemd/system/northstar.service  
sudo systemctl daemon-reload  
sudo systemctl restart northstar  
sudo systemctl status northstar

### **RDS Problems**

* Security group configuration- RDS configuration in instance security group is easy but the instance security group in RDS security group is showing errors while connecting through ec2 security group, why?  
* RDS can be connected but the ec2 doesn't have any DBMS to access on the server  
* Connecting load balancer to RDS which is inside private subnet, how to do it

Troubleshooting  
Cannot connect to the RDS

1) Check the database port is allowed in the instance security group, this cause connection timeout   
2) Check the ec2 instance security group is allowed in RDS security group, it shows connection refused  
3) Check the port number because each database has different port numbers

Connection timed out

1) Check the database is available because it take some time for creating, configuring and backing

RDS connected to instance, to test

1) Sudo psql, correct end point ,port number, username, password, database name  
2) Check whether it is correct because it may cause connection time out

Security group troubleshoot

1) Delete the inbound of errored rule and add new rule and connect the Ec2 security group again, but i dont know why it is happening 

![image alt](https://github.com/Shibisaran/Northstar-Aws-Launch/blob/8179852f4aee1d27de83f92694cc1d1a25dd8ca6/screenshots/img5.jpg)  
![][image5]  
![][image6]  
![][image7]  


