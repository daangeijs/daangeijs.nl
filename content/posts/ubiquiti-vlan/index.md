---
title: "Setting Up an Isolated Virtual Server in a VLAN on Ubiquiti and Proxmox"
date: 2023-06-14T12:48:00+01:00
draft: false

tags:
- ubiquiti
- proxmox
- postgresql
- security

cover:
    image: "cover.png"
    alt: "Proxmox Logo"

summary:
    Hosting your own services to be accessed by the public internet comes with its share of challenges, especially when exposing ports security concerns are involved. Cloud hosting providers are a good way to solve some of these problems, but can the costs can rise pretty quickly.
---
Hosting your own services to be accessed by the public internet comes with its share of challenges, especially when exposing ports security concerns are involved. Cloud hosting providers are a good way to solve some of these problems, but can the costs can rise pretty quickly. 

In this article I wrote down a  step-by-step walkthrough on creating an isolated environment for hosting services, using a VLAN setup.  By using a VLAN and setting up a firewall we can isolate the virtual server from your primary private network, layering an additional shield of security to your setup. As an example we'll use a virtual machine (VM) hosting a database service as our primary example.
### Ubiquiti VLAN Configuration

#### 1. **Create a VLAN**:

-   Log into your **UniFi Controller**.
-   Navigate to the "Settings" (gear icon) at the bottom left.
-   Under "Networks", click on "Create New Network".
-   Provide a name for the network, for instance, "PostgreSQL VLAN".
-   Set "Purpose" to "Corporate".
-   Assign a VLAN ID of "10".
-   Define the subnet as `10.0.0.1/24`.
-   Configure the DHCP range if required and save these settings.

#### 2. **Firewall Rules for VLAN Traffic**:

-   Proceed to "Routing & Firewall" within the settings.
-   Select "Firewall" and then "LAN IN".
-   Set up a rule that permits PostgreSQL traffic:
    
    -   Name: **Allow PostgreSQL to WAN**
    -   Action: **Accept**
    -   Source: **PostgreSQL VLAN**
    -   Destination: **Any**
    -   Ports: **5432** (PostgreSQL's default port)
-   Create rules that block all traffic from the VLAN to other local networks:
    
    -   Name: **Block VLAN to all LANs**
    -   Action: **Drop**
    -   Source: **PostgreSQL VLAN**
    -   Destination: **All other local networks/VLANs**

#### 3. **Port Forwarding** (only if you're planning on exposing the PostgreSQL server to the internet):

-   Navigate to "Routing & Firewall" and select "Port Forwarding".
-  Click on the "+ Create New Rule" or "Add New Port Forward Rule" button, which should open a new window or pane for rule creation.

-   **Name**: Give the rule a descriptive name, e.g., "PostgreSQL Remote Access".
-   **Enabled**: Make sure this is toggled on.
-   **Rule Applied**: Typically set to "Before Predefined Rules" unless you have specific needs.
-   **WAN Interface**: Usually set to "All" unless you have multiple WANs and prefer a specific one.
-   **Original IP**: Leave as "Any" to allow access from any external IP or specify a range/IP if you have a static IP where you'll be connecting from.
-   **Original Port**: Set to the PostgreSQL default port, "5432".
-   **Forward IP**: Enter the IP address of the machine where PostgreSQL is running, in this case, the VM's IP, `10.0.0.2`.
-   **Forward Port**: Again, set this to "5432".
-   **Protocol**: PostgreSQL typically uses TCP, so set this to "TCP". If there are any reasons to believe you need both TCP and UDP, you can set it to "Both", but this is usually not necessary for PostgreSQL.

### Proxmox VM Configuration

1.  **VM Creation or Modification**:
    
    -   Access the Proxmox web interface.
    -   Either initiate a new VM or select an existing one.
    -   During the setup or via the "Network" menu for an existing VM:
        -   Set the "Model" to VirtIO (or another preferred model).
        -   Use the default bridge, typically `vmbr0`.
        -   Assign the "VLAN Tag" to "10".
        -   Ensure the firewall is activated.
2.  **Static IP Configuration**:
    
    -   Whether you're initiating a new VM or adjusting an existing one, configure the static IP address within the network settings:
        -   **IPv4/CIDR**: `10.0.0.2/32`
        -   **Gateway**: `10.0.0.1`
    -   Once the VM is started or rebooted, it should automatically acquire the assigned static IP.

### Testing the Configuration

1.  **Verify the IP Address**:
    
    -   In Proxmox, access the VM's console.
    -   Execute the `ifconfig` command to ensure that the IP address `10.0.0.2` has been correctly assigned.
2.  **Test Connectivity**:
 
    -   In the same console, check internet access by pinging an external website: `ping www.daangeijs.nl`.
    -   Subsequently, attempt to ping a device from your private network. This ping should fail, verifying that the VM is isolated from the private network.