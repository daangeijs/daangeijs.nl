---
title: "Proxmox: how to Expand Storage in a Linux VM with LVM"
date: 2023-05-25T12:48:00+01:00
draft: false

tags:
- ubuntu
- docker
- proxmox
- lvm

cover:
    image: "cover.png"
    alt: "Proxmox Logo"

summary:
   After bolstering the storage capacity of a Linux VM within Proxmox or another hypervisor, you'll discover that the operating system inside the VM doesn't automatically recognize or utilize this newly added space.
---
#### Introduction

**Problem**: 
After bolstering the storage capacity of a Linux VM within Proxmox or another hypervisor, you'll discover that the operating system inside the VM doesn't automatically recognize or utilize this newly added space.

**Solution**: 
To harness this additional storage, you need to resize both the partitions and the filesystems within the Linux environment. If you've configured your VM with Logical Volume Management (LVM), this entails adjusting the physical volume, the logical volume, and subsequently, the filesystem.

1. **Ensure the Partition Covers the New Space**:
   
   To observe the current partitions:
   ```bash
   sudo fdisk -l
   ```

   **Example Output**:
   ```
   Device     Start      End  Sectors  Size Type
   /dev/sda1   2048   999423   997376  487M EFI System
   /dev/sda2 999424 20479999 19480576  9.3G Linux filesystem
   ```
   
   If, for instance, `/dev/sda2` isn't leveraging the entire disk space, you need to adjust it. Here's how:
   
   Launch the partition tool for the disk:
   ```bash
   sudo fdisk /dev/sda
   ```
   - Press `p` to display the existing partition layout.
   - Ensure you note the start sector of the partition you intend to resize.
   - Press `d` to delete the desired partition, and select its number (like `2` for `/dev/sda2`).
   - Hit `n` to create a new partition. Use the exact start sector from earlier and allow the default end sector to encompass all available space.
   - Press `t` to modify the partition type and assign it to `8e`, denoting Linux LVM.
   - To apply the changes, press `w`.

   **Example Output**:
   ```
   Command (m for help): n
   Partition number (2-4, default 2): 2
   First sector (999424-49971199, default 999424): 999424
   Last sector, +/-sectors or +/-size{K,M,G,T,P} (999424-49971199, default 49971199): 
   Created a new partition 2 of type 'Linux filesystem' and of size 23.3 GiB.
   ```

2. **Inform the Kernel About Partition Changes**:
   
   ```bash
   sudo partprobe
   ```

3. **Expand the LVM Physical Volume**:
   
   To view the current status:
   ```bash
   sudo pvdisplay
   ```
   **Example Output**:
   ```
   --- Physical volume ---
   PV Name               /dev/sda2
   VG Name               ubuntu-vg
   PV Size               9.30 GiB
   ```

   To resize the physical volume:
   ```bash
   sudo pvresize /dev/sda2
   ```

4. **Expand the LVM Logical Volume**:
   
   ```bash
   sudo lvresize -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
   ```

5. **Resize the Filesystem**:

   ```bash
   sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
   ```

6. **Verify the Changes**:
   
   ```bash
   df -h
   ```

   **Example Output**:
   ```
   Filesystem                             Size  Used Avail Use% Mounted on
   /dev/mapper/ubuntu--vg-ubuntu--lv      23G  4.8G   17G  22% /
   ```

#### LVM vs. Logical Volume: What's the Difference?

LVM (Logical Volume Management) offers a flexible and agile solution for storage management, enabling the seamless management of disk drives and similar storage mechanisms. Under the LVM umbrella, you'll encounter:

- **Physical Volumes (PV)**: These are your raw storage devices or partitions that store data.
- **Volume Groups (VG)**: Collections of physical volumes, they act as one consolidated storage reservoir.
- **Logical Volumes (LV)**: These lie within a volume group and act as block devices that sustain the filesystem.

In essence, LVM facilitates the amalgamation of several disks (or partitions) into a singular storage pool (VG). From this pool, logical subdivisions (LVs) can be extracted, upon which filesystems are created.

Thus, when we discuss "expanding LVM", we're essentially alluding to a series of tasks that incorporate expanding the physical volume (PV), possibly the volume group (VG), followed by the logical volume (LV). Only post these operations is the filesystem itself stretched to occupy the new space.

---

Endowed with these precise commands and sample outputs, you're equipped with a clear roadmap of what to anticipate at every juncture. As a precaution, always ensure your data is backed up before initiating any significant modifications to your storage structures.
