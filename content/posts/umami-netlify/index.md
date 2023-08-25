---
title: "Website Analytics with Umami, Netlify and a self-hosted database. "
date: 2023-08-22T12:48:00+01:00
draft: false

tags:
- proxmox
- netlify
- umami
- postgresql

cover:
    image: "umami.jpg"
    alt: "Umami Logo"
    hidden: true

summary:
    Umami is a sleek, open-source analytics tool that provides an alternative to mainstream solutions like Google Analytics. Its simplicity and transparency make it a preferred choice for those wary of the intricacies and potential privacy concerns associated with bigger platforms.
---
{{< figure src="cover.jpg" >}}
Umami is a sleek, open-source analytics tool that provides an alternative to mainstream solutions like Google Analytics. Its simplicity and transparency make it a preferred choice for those wary of the intricacies and potential privacy concerns associated with bigger platforms. 

In this case I like having autonomy and control of hosting my own data, but I also appreciate the efficiency and scalability of cloud services. That's why, I've opted to host the database needed for Umami at home on my homeserver using Proxmox.  However, when it comes to the dashboard – the visual heart of Umami – I use Netlify. Hosting the Umami dashboard on Netlify not only offloads my trusty NUC from running yet another service but also made installation a breeze with Netlify's effortless deployment process. In this article I will show you how I set it up.

## Setting Up Database on Proxmox

1. **Download CT Template**: Begin by obtaining the `turnkey-postgresql` CT template. The easiest way to do this is to download the template from the Proxmox web interface. Navigate to "Templates" -> "Download" and search for "turnkey-postgresql". Select the template and click "Download".

2. **Create a LXC container**:
{{< figure src="1.png" >}}
   - Assign a fixed IP address (fixed to enable port forwarding).
   - Allocate 1024MB memory and 1024MB swap.
   - Dedicate 1 CPU core.
   - Designate 16GB for disk storage.
   - Ensure "start after created" is selected.

For me these where the resources that I had available, but you can adjust these to your own needs.

3. **Complete Initialization**: Access the console of your started container, log in with `root` and the password you set up at the previous step. Complete the installation, skipping any unnecessary add-ons but making sure to apply the updates.
{{< figure src="3.png" >}}
4. **Database Setup**: Navigate to the browser using assigned-static-IP-address:12322 or simply input the IP address. This will take you to a dashboard where you can select Adminer. Use Adminer to log in with PostgreSQL credentials. Create a table named `umami`.
{{< figure src="5.png" >}}
5. **Port forwarding** Make sure you don't forget to enable port forwarding (5432) to the IP address of your running Postgres container. Ofcourse, this completely depends on your network setup. Keep in mind that exposing a port does come with security vulnerabilities. If you have an Ubiquiti router [you can read this article]( {{< relref "ubiquiti-vlan" >}}) for more information on how to set this up in a more safe way.

## Deploying Umami on Netlify

1. **Fork Repository**: Fork the Umami repository to your GitHub account: 
      ```html
      https://github.com/umami-software/umami
      ```

2. **Netlify Setup**:
   - Log into Netlify.
   - Choose "Add New Site" -> "Import Existing Site".
   - Opt for "Deploy with GitHub".
   - Select your forked Umami repository.

3. **Environment Variable**:
{{< figure src="6.png" >}}
   - In the site settings of your new project, navigate to "Site configuration" -> "Environment variables".
   - Add the `DATABASE_URL` variable with the value:
     ```html
     postgresql://<postgres_account>:<postgress_password>@<your_db_ip>/umami
     ```

4. **Trigger Deployment**:
{{< figure src="7.png" >}}
   - In the Netlify dashboard, go to "Deploys".
   - Select "Trigger Deploy" and choose "Clear cache and deploy site".


The example here is just with Proxmox, but you can choose any popular solutions like AWS, Azure, DigitalOcean, or Heroku— provided they support PostgreSQL.  At the end you just need to update the URL in the Netlify dashboard.  Choose what's best for your needs.