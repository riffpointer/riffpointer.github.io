---
layout: post
title: macOS High Sierra on QEMU Installation Notes (OSX-KVM)
date: "2026-06-24 00:00:00 +05:30"
categories: [emulation, linux, macos]
tags: [macos, hackintosh, qemu, emulation, linux, kvm]
---
This guide provides instructions to install and configure a macOS High Sierra (10.13) virtual machine using the OSX-KVM repository on a Fedora Linux host. The hardware configuration used for these steps is an AMD Ryzen 5 5600X processor and an NVIDIA RTX 5060 graphics card with 16GB of RAM.

## Host environment and prerequisites

Run the following command in the Fedora terminal to install the packages required for QEMU, KVM, and image processing:

```bash
sudo dnf install qemu-kvm qemu-img libvirt virt-manager git dmg2img python3 python3-pip
```

Ensure that the virtualization kernel modules are loaded and that your user account has permissions to run KVM by adding the user to the libvirt group:

```bash
sudo usermod -aG libvirt $USER
```

Log out and log back into Fedora for the group changes to take effect.

---

## Downloading the installation media

Clone the OSX-KVM repository from GitHub and move into the project directory:

```bash
git clone https://github.com/kholia/OSX-KVM.git
cd OSX-KVM
```

Run the interactive Python script to fetch the macOS installation files from Apple servers:

```bash
python3 fetch-macOS-v2.py
```

The script displays a list of available macOS versions. Type the number corresponding to High Sierra and press Enter. The script downloads a file named `BaseSystem.dmg`.

Convert the downloaded Apple disk image into a raw image format that QEMU can read using the `dmg2img` utility:

```bash
dmg2img BaseSystem.dmg BaseSystem.img
```

---

## Creating the virtual storage drive

Create a virtual hard disk file where the macOS operating system will be installed. The file format is `qcow2` and the designated size is 64 gigabytes:

```bash
qemu-img create -f qcow2 mac_hdd_ng.qcow2 64G
```

---

## Modifying the launch script for hardware compatibility

The NVIDIA RTX 5060 does not have drivers in macOS High Sierra, so the virtual machine must use CPU software rendering. The default input and network configurations in the repository are also incompatible with High Sierra on AMD hardware.

Open the `OpenCore-Boot.sh` file in a text editor to apply the necessary hardware parameters:

```bash
nano OpenCore-Boot.sh
```

### Input device changes

Locate the section defining the input devices. Replace those lines with the configuration below to attach the devices directly to the native root ports of the virtual motherboard:

```bash
-usb \
-device usb-kbd \
-device usb-tablet \
```

### Network card changes

Locate the line containing the network parameters. Change the device model from `virtio-net-pci` to `e1000-82545em` to emulate a network card that macOS High Sierra supports natively:

```bash
-netdev user,id=net0,hostfwd=tcp::2222-:22 -device e1000-82545em,netdev=net0,id=net0,mac=52:54:00:c9:18:27
```

### Video display and monitor redirection changes

Locate the display device parameters. Update them to use the SDL backend with OpenGL support to clear text bugs and reduce screen tearing:

```bash
-device vmware-svga -display sdl,gl=es
```

Locate the parameter `-monitor stdio` and change it to the following text to prevent terminal debug strings from printing directly over the graphical window buffer:

```bash
-monitor vc
```

Save the file and exit the text editor.

---

## Bypassing recovery server connection errors

Execute the modified script to start the virtual machine:

```bash
./OpenCore-Boot.sh
```

In the OpenCore boot menu, select the option to boot the macOS base system installer.

The macOS installer verifies security certificates that are expired relative to the current date on your host system. This causes an error stating that the recovery server could not be contacted.

To bypass this error, click Utilities in the top menu bar of the installer screen, then click Terminal. Run this command to redirect the installer catalog to an unencrypted HTTP address:

(Unfortunately you have to type this whole thing in manually)

```bash
nvram IASUCatalogURL="http://swscan.apple.com/content/catalogs/others/index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
```

Run this command in the same terminal window to set the system date back to October 25, 2017:

```bash
date 1025120017
```

Type `exit`, close the terminal window, and open Disk Utility. Format the virtual storage drive (`mac_hdd_ng.qcow2`) as Mac OS Extended (Journaled) with a GUID Partition Map. Close Disk Utility, select Reinstall macOS, and proceed with the installation steps.

---

## Modifying the OpenCore configuration on Fedora

If the OpenCore bootloader displays syntax errors or needs configuration adjustments, you must modify its `config.plist` file directly on the Fedora host.

Turn off the macOS virtual machine before executing these commands. Run the following commands in the Fedora terminal to load the network block device module and mount the OpenCore disk image partition:

```bash
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect=/dev/nbd0 ./OpenCore/OpenCore.qcow2
mkdir -p ~/opencore_efi
sudo mount /dev/nbd0p1 ~/opencore_efi
```

Open the configuration file with a text editor:

```bash
sudo nano ~/opencore_efi/EFI/OC/config.plist
```

To clear the background screen memory when the graphical interface loads, locate the `ClearScreenOnModeSwitch` key and set its value to true:

```xml
<key>ClearScreenOnModeSwitch</key>
<true/>
```

Locate the UEFI section and find the `ConnectDrivers` key. Ensure that the `Drivers` key underneath it maps to an array block. Remove any empty dictionary blocks (`<dict></dict>`) that sit between the `ConnectDrivers` key and the `Drivers` array to prevent syntax interpretation errors.

Save the changes and exit the text editor. Disconnect the virtual drive safely before launching the virtual machine again:

```bash
sudo umount ~/opencore_efi
sudo qemu-nbd --disconnect /dev/nbd0
```