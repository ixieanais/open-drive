<div align="center">

<img src="docs/logo.png" width="150" height="150">

# OpenDrive

**A lightweight, self-hosted cloud storage system built for full data ownership**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)

</div>

# Overview

OpenDrive is a self-hosted cloud storage solution designed to give you complete control over your data. No third-party servers, no subscriptions — just your files, on your machine.

Inspired by the simplicity and clean interface of [GNOME Files](https://apps.gnome.org/Nautilus/), OpenDrive offers a similarly intuitive interface in its web version—familiar, unobtrusive.

Built with simplicity and ease of use in mind, OpenDrive is the ideal choice for anyone who wants a clean, private, and fully self-managed alternative to mainstream cloud storage.

# Installation

```bash
git clone https://github.com/ixieanais/open-drive
cd open-drive
pip install -r requirements.txt
```

Configure your database connection:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=opendrive
DB_USER=your_user
DB_PASSWORD=your_password
```

# Usage

> [!IMPORTANT]
> Make sure PostgreSQL is running

Run the `main.py`, open browser and open the window with this link: http://localhost:8080

# License

Copyright © 2026 [ixieanais](https://github.com/ixieanais). <br>
OpenDrive is [MIT](https://choosealicense.com/licenses/mit) licensed.